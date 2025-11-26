# -*- coding: utf-8 -*-
import os
from pyrevit import forms
import Autodesk
from Autodesk.Revit.DB import (
    FilteredElementCollector,
    BuiltInCategory,
    PrintRange
)

PDF_DRIVER = "PDFCreator"


def run(uiapp, data, log):
    try:
        uidoc = uiapp.ActiveUIDocument
        doc = uidoc.Document

        sheet_ids = data.get("sheet_ids", [])
        export_path = data.get("path", r"C:\PADApps\RevitPAD\ExportsPDF")

        if not os.path.exists(export_path):
            os.makedirs(export_path)

        log("PRINT-CURRENT-WINDOW mode started")
        log("Sheet IDs received: {0}".format(sheet_ids))

        # --------------------------------------------
        # Collect sheets
        # --------------------------------------------
        collector = FilteredElementCollector(doc)\
            .OfCategory(BuiltInCategory.OST_Sheets)\
            .WhereElementIsNotElementType()

        sheets = [s for s in collector if s.Id.IntegerValue in sheet_ids]
        log("Filtered sheets = {0}".format(len(sheets)))

        if not sheets:
            forms.alert("No matching sheets found.")
            return

        # --------------------------------------------
        # Configure PDF print driver
        # --------------------------------------------
        pm = doc.PrintManager
        pm.SelectNewPrintDriver(PDF_DRIVER)
        pm.PrintToFile = True
        pm.PrintRange = PrintRange.Current

        exported = []

        # --------------------------------------------
        # Main loop — one sheet at a time
        # --------------------------------------------
        for sheet in sheets:

            # 1) SWITCH ACTIVE VIEW (NO TRANSACTION)
            log("→ Activating sheet {}".format(sheet.SheetNumber))
            uidoc.ActiveView = sheet  # THIS MUST BE OUTSIDE ANY TRANSACTION

            # Revit needs a tiny processing yield to fully activate view
            uiapp.PostCommand   # no-op to yield to UI

            # 2) Build safe filename
            num = sheet.SheetNumber
            name = sheet.Name
            combined = "{0}_{1}".format(num, name)
            safe = "".join([c for c in combined if c.isalnum() or c in ("_", "-")])
            output = os.path.join(export_path, safe + ".pdf")

            log("→ Printing to: {0}".format(output))

            # 3) Configure output filename
            pm.PrintToFileName = output
            pm.Apply()

            # 4) Print current active sheet
            pm.SubmitPrint()
            log("✔ Printed: {}".format(output))
            exported.append(output)

        # --------------------------------------------
        msg = "PDF Export complete → {} files".format(len(exported))
        log(msg)
        forms.alert(msg)

    except Exception as e:
        log("PDF Export error: {}".format(e))
        forms.alert("PDF Export error:\n{}".format(e))
