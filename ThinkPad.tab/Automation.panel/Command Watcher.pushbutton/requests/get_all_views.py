# -*- coding: utf-8 -*-
import os
import json
from Autodesk.Revit.DB import (
    FilteredElementCollector,
    View
)

REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
RESPONSE_PATH = os.path.join(DATA_FOLDER, "response.json")


def run(uiapp, data, log):
    """
    Returns ALL non-template views in the model.
    Grouped by general view type.
    """
    try:
        doc = uiapp.ActiveUIDocument.Document

        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

        # Prepare container for grouping
        views_by_type = {}

        collector = FilteredElementCollector(doc).OfClass(View)

        for v in collector:
            try:
                if v.IsTemplate:
                    continue

                vtype = str(v.ViewType)

                if vtype not in views_by_type:
                    views_by_type[vtype] = []

                views_by_type[vtype].append({
                    "id": v.Id.IntegerValue,
                    "name": v.Name,
                    "view_type": vtype
                })

            except Exception:
                pass

        result = {"views": views_by_type}

        with open(RESPONSE_PATH, "w") as f:
            json.dump(result, f, indent=2)

        log("Returned all views grouped by type.")

    except Exception as e:
        # Return error
        with open(RESPONSE_PATH, "w") as f:
            json.dump({"error": str(e)}, f, indent=2)

        log("Error in get_all_views: {0}".format(e))
