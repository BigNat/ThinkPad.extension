# -*- coding: utf-8 -*-
import os, json
from pyrevit import forms
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory

REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")



def run(uiapp, data, log):
    """Exports all Revit sheets to JSON file."""
    try:
        doc = uiapp.ActiveUIDocument.Document
        base_dir = DATA_FOLDER
        output_path = os.path.join(base_dir, "data.json")

        sheets = []
        for s in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets):
            try:
                sheets.append({
                    "id": s.Id.IntegerValue,
                    "sheet_number": s.SheetNumber,
                    "sheet_name": s.Name
                })
            except Exception:
                pass

        with open(output_path, "wb") as f:
            txt = json.dumps({"sheets": sheets}, indent=2, ensure_ascii=False)
            f.write(txt.encode("utf-8"))

        msg = "✅ Exported {0} sheets → {1}".format(len(sheets), output_path)
        log(msg)
        forms.alert(msg, title="Revit Command Watcher")

    except Exception as e:
        log("Error in export_sheets_to_json: {0}".format(e))
