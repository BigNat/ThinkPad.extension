# -*- coding: utf-8 -*-
import os
import json
from pyrevit import forms
from Autodesk.Revit.DB import (
    FilteredElementCollector,
    BuiltInCategory,
    PrintRange
)

PDF_DRIVER = "PDFCreator"

REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
RESPONSE_PATH = os.path.join(DATA_FOLDER, "response.json")


def write_response(payload, log):
    """Safe writer for the Revit response.json."""
    try:
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)
        with open(RESPONSE_PATH, "w") as f:
            json.dump(payload, f, indent=2)
        log("Response.json written.")
    except Exception as e:
        log("ERROR writing response.json: {}".format(e))


def run(uiapp, data, log):
    """
    Export sheets to PDF and write a RevitPAD response.json
    """
    try:
        uidoc = uiapp.ActiveUIDocument
        doc = uidoc.Document

        # ---------------------------------------------------
        # Incoming request data
        # ---------------------------------------------------
        sheet_ids = data.get("sheet_ids", [])
        export_path = data.get("path", r"C:\PADApps\RevitPAD\ExportsPDF")

        if not os.path.exists(export_path):
            os.makedirs(export_path)

        if not sheet_ids:
            msg = "No sheet_ids passed to export_sheets_to_pdf"
            log(msg)
            write_response({"error": msg}, log)
            return

        log("PRINT-CURRENT-WINDOW mode started")
        log("Sheet IDs received: {}".format(sheet_ids))

        # ---------------------------------------------------
        # Collect matching sheets
        # ---------------------------------------------------
        collector = (
            FilteredElementCollector(doc)
            .OfCategory(BuiltInCategory.OST_Sheets)
            .WhereElementIsNotElementType()
        )

        sheets = [s for s in collector if s.Id.IntegerValue in sheet_ids]

        if not sheets:
            msg = "No valid sheets found for provided IDs."
            log(msg)
            write_response({"error": msg}, log)
            return

        # ---------------------------------------------------
        # Configure PDF print driver
        # ---------------------------------------------------
        pm = doc.PrintManager
        pm.SelectNewPrintDriver(PDF_DRIVER)
        pm.PrintToFile = True
        pm.PrintRange = PrintRange.Current

        exported = []

        # ---------------------------------------------------
        # Loop — one sheet per file
        # ---------------------------------------------------
        for sheet in sheets:
            log("→ Activating sheet {}".format(sheet.SheetNumber))

            # Activate sheet
            uidoc.ActiveView = sheet

            # Make filename
            num = sheet.SheetNumber
            name = sheet.Name
            combined = "{}_{}".format(num, name)
            safe = "".join([c for c in combined if c.isalnum() or c in ("_", "-")])

            out_file = os.path.join(export_path, safe + ".pdf")
            log("→ Printing to: {}".format(out_file))

            pm.PrintToFileName = out_file
            pm.Apply()
            pm.SubmitPrint()

            log("✔ Printed: {}".format(out_file))
            exported.append(out_file)

        # ---------------------------------------------------
        # Write success response
        # ---------------------------------------------------
        payload = {
            "status": "ok",
            "exported_count": len(exported),
            "exported_files": exported
        }

        write_response(payload, log)
        log("PDF Export complete → {} files".format(len(exported)))

    except Exception as e:
        err = "PDF Export error: {}".format(e)
        log(err)
        write_response({"error": err}, log)
