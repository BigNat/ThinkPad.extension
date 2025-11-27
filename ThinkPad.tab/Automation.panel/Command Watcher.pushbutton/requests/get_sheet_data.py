# -*- coding: utf-8 -*-
import os
import json
from Autodesk.Revit.DB import (
    FilteredElementCollector,
    BuiltInCategory,
    BuiltInParameter,
    Revision
)

REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
RESPONSE_PATH = os.path.join(DATA_FOLDER, "response.json")


def run(uiapp, data, log):
    """
    Request handler: returns all Revit sheets and revision metadata.
    Writes output to response.json for BlueTree to read.
    """
    try:
        doc = uiapp.ActiveUIDocument.Document

        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

        sheets_out = []

        collector = FilteredElementCollector(doc).OfCategory(
            BuiltInCategory.OST_Sheets
        )

        for s in collector:
            try:
                # --- Current revision number ---
                rev_param = s.get_Parameter(BuiltInParameter.SHEET_CURRENT_REVISION)
                current_rev_num = rev_param.AsString() if rev_param else None
                if not current_rev_num:
                    current_rev_num = None

                rev_desc = None
                rev_date = None

                # --- Match the Revision element ---
                if current_rev_num:
                    for rev_id in s.GetAllRevisionIds():
                        rev = doc.GetElement(rev_id)
                        if isinstance(rev, Revision) and rev.RevisionNumber == current_rev_num:
                            rev_desc = rev.Description
                            rev_date = rev.RevisionDate
                            break

                sheets_out.append({
                    "id": s.Id.IntegerValue,
                    "sheet_number": s.SheetNumber,
                    "sheet_name": s.Name,
                    "revision_number": current_rev_num,
                    "revision_description": rev_desc,
                    "revision_date": rev_date
                })

            except Exception:
                pass

        # --- Write request result ---
        result = {"sheets": sheets_out}

        with open(RESPONSE_PATH, "w") as f:
            json.dump(result, f, indent=2)

        log("Returned sheet data: {0} sheets".format(len(sheets_out)))

    except Exception as e:
        log("Error in get_sheet_data: {0}".format(e))
