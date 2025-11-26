# -*- coding: utf-8 -*-
import os, json
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory

def run(uiapp, data, log):
    doc = uiapp.ActiveUIDocument.Document

    base_dir = os.path.dirname(data.get("watch_path", ""))
    out_file = os.path.join(base_dir, "revit_sheets.json")

    sheets = []
    for s in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets):
        sheets.append({
            "id": s.Id.IntegerValue,
            "sheet_number": s.SheetNumber,
            "sheet_name": s.Name
        })

    # IronPython-friendly file write
    with open(out_file, "wb") as f:
        txt = json.dumps({"sheets": sheets}, indent=2, ensure_ascii=False)
        f.write(txt.encode("utf-8"))

    # IronPython-safe logging
    log("Exported {0} sheets.".format(len(sheets)))

    return {"status": "ok", "count": len(sheets)}
