# -*- coding: utf-8 -*-
import os, json
from pyrevit import forms
from Autodesk.Revit.DB import (
    FilteredElementCollector,
    BuiltInCategory,
    ViewSet,
    PrintRange
)

PDF_DRIVER = "PDFCreator"   # ← your installed PDF driver

def run(uiapp, data, log):
    try:
        doc = uiapp.ActiveUIDocument.Document

        sheet_ids = data.get("sheet_ids", [])
        export_path = data.get("path", r"C:\PADApps\RevitPAD\ExportsPDF")

        if not os.path.exists(export_path):
            os.makedirs(export_path)

        log("Starting export_sheets_to_pdf → {0}".format(export_path))
        log("Sheets to export: {0}".format(len(sheet_ids)))

        # -----------------------------
        # Collect target sheets
        # -----------------------------
        all_sheets = FilteredElementCollector(doc) \
            .OfCategory(BuiltInCategory.OST_Sheets) \
            .WhereElementIsNotElementType()

        if sheet_ids:
            sheets = [s for s in all_sheets if s.Id.IntegerValue in sheet_ids]
        else:
            sheets = list(all_sheets)

        if not sheets:
            log("⚠️ No matching sheets found.")
            forms.alert("No valid sheets to export.")
            return

        # -----------------------------
        # Configure PrintManager
        # -----------------------------
        pm = doc.PrintManager
        pm.SelectNewPrintDriver(PDF_DRIVER)
        pm.Apply()

        pm.PrintToFile = True
        pm.PrintRange = PrintRange.Select

        vss = pm.ViewSheetSetting
        exported = []

        # -----------------------------
        # PDF Export Loop
        # -----------------------------
        for sheet in sheets:
            try:
                num = sheet.SheetNumber
                name = sheet.Name

                # IronPython-safe name building
                combined = "{0}_{1}".format(num, name)
                safe = "".join([c for c in combined if c.isalnum() or c in ("_", "-")])
                output = os.path.join(export_path, safe + ".pdf")

                log("→ Exporting PDF: {0}".format(output))

                # 1. Build ViewSet
                vs = ViewSet()
                vs.Insert(sheet)

                # 2. Apply the ViewSet
                vss.CurrentViewSheetSet.Views = vs
                pm.Apply()

                # 3. Tell driver where to save
                pm.PrintToFileName = output
                pm.CombinedFile = False
                pm.Apply()

                # 4. Export
                pm.SubmitPrint()

                exported.append(output)
                log("✔ PDF Exported: {0}".format(output))

            except Exception as e:
                log("❌ Failed: {0} → {1}".format(num, e))

        msg = "PDF Export complete: {0} files\n{1}".format(len(exported), export_path)
        log(msg)
        forms.alert(msg)

    except Exception as e:
        log("💥 Error in export_sheets_to_pdf: {0}".format(e))
