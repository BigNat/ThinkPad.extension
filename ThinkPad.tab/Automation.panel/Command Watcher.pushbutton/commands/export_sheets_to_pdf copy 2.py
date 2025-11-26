# -*- coding: utf-8 -*-
import os, json
from pyrevit import forms
import Autodesk
from Autodesk.Revit.DB import (
    FilteredElementCollector,
    BuiltInCategory,
    ViewSet,
    PrintRange,
    Transaction,
    ViewSheetSetting,
    ViewSheetSet,
    ViewSheetSetElement,
    ViewSet,
    ElementId
)

PDF_DRIVER = "PDFCreator"


def run(uiapp, data, log):
    try:
        doc = uiapp.ActiveUIDocument.Document

        sheet_ids = data.get("sheet_ids", [])
        export_path = data.get("path", r"C:\PADApps\RevitPAD\ExportsPDF")

        if not os.path.exists(export_path):
            os.makedirs(export_path)

        log("Starting export_sheets_to_pdf → {0}".format(export_path))
        log("Sheet IDs: {0}".format(sheet_ids))

        # ----------------------------------
        # Collect ONLY selected sheets
        # ----------------------------------
        all_sheets = FilteredElementCollector(doc)\
            .OfCategory(BuiltInCategory.OST_Sheets)\
            .WhereElementIsNotElementType()

        target_sheets = [s for s in all_sheets if s.Id.IntegerValue in sheet_ids]

        log("Filtered sheets count = {0}".format(len(target_sheets)))

        if not target_sheets:
            forms.alert("No valid sheets selected.")
            return

        # ----------------------------------
        # Configure PrintManager
        # ----------------------------------
        pm = doc.PrintManager
        pm.SelectNewPrintDriver(PDF_DRIVER)
        pm.Apply()

        pm.PrintToFile = True
        pm.PrintRange = PrintRange.Select

        exported = []

        # ----------------------------------
        # Loop sheets one-by-one
        # ----------------------------------
        for sheet in target_sheets:

            num = sheet.SheetNumber
            name = sheet.Name
            combined = "{0}_{1}".format(num, name)
            safe_name = "".join([c for c in combined if c.isalnum() or c in ("_", "-")])
            out_path = os.path.join(export_path, safe_name + ".pdf")

            log("→ Exporting: {}".format(out_path))

            #-----------------------------------------------
            # Create ViewSet
            #-----------------------------------------------
            vs = ViewSet()
            vs.Insert(sheet)

            #-----------------------------------------------
            # Create a TEMP Print Set
            #-----------------------------------------------
            temp_set_name = "BlueTreeTempSet"

            t = Transaction(doc, "Create Temporary Print Set")
            t.Start()

            vss = pm.ViewSheetSetting

            # If a temp set exists, remove it
            try:
                existing = vss.CurrentViewSheetSet
                if existing and existing.Name == temp_set_name:
                    vss.Delete()
            except:
                pass

            # Create a new temp set
            vss.CurrentViewSheetSet.Views = vs
            vss.SaveAs(temp_set_name)

            t.Commit()

            #-----------------------------------------------
            # Assign output file & print
            #-----------------------------------------------
            pm.PrintToFileName = out_path
            pm.CombinedFile = False
            pm.Apply()

            pm.SubmitPrint()
            exported.append(out_path)

            log("✔ Exported: {0}".format(out_path))

            #-----------------------------------------------
            # Delete the temporary print set
            #-----------------------------------------------
            t2 = Transaction(doc, "Delete Temporary Print Set")
            t2.Start()

            try:
                vss.Delete()
            except:
                pass

            t2.Commit()

        # ----------------------------------
        # FINISHED
        # ----------------------------------
        msg = "PDF Export complete → {} files".format(len(exported))
        log(msg)
        forms.alert(msg)

    except Exception as e:
        log("💥 Error in export_sheets_to_pdf: {}".format(e))
        forms.alert("PDF Export Error:\n{}".format(e))
