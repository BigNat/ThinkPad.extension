# -*- coding: utf-8 -*-
import os
import json
from Autodesk.Revit.DB import (
    FilteredElementCollector,
    View3D
)

REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
RESPONSE_PATH = os.path.join(DATA_FOLDER, "response.json")


def run(uiapp, data, log):
    """
    Returns all 3D views in the current Revit document.
    Includes id, name, view type, and perspective flag.
    """
    try:
        doc = uiapp.ActiveUIDocument.Document

        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

        views = []
        collector = FilteredElementCollector(doc).OfClass(View3D)

        for v in collector:
            try:
                # Skip templates
                if v.IsTemplate:
                    continue

                views.append({
                    "id": v.Id.IntegerValue,
                    "name": v.Name,
                    "is_perspective": bool(v.IsPerspective),
                    "view_type": str(v.ViewType)
                })
            except Exception:
                pass

        result = {"views": views}

        with open(RESPONSE_PATH, "w") as f:
            json.dump(result, f, indent=2)

        log("Returned 3D views: {0}".format(len(views)))

    except Exception as e:
        with open(RESPONSE_PATH, "w") as f:
            json.dump({"error": str(e)}, f, indent=2)
        log("Error in get_3d_views: {0}".format(e))
