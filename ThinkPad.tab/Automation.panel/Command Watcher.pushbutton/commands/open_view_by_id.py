# -*- coding: utf-8 -*-
import os
import json
from Autodesk.Revit.DB import ElementId

REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
RESPONSE_PATH = os.path.join(DATA_FOLDER, "response.json")


def run(uiapp, data, log):
    """
    Opens a view in Revit by its element ID.
    """
    try:
        doc = uiapp.ActiveUIDocument.Document
        view_id_int = data.get("id")

        if not view_id_int:
            raise Exception("Missing 'id' field for open-view-by-id")

        # Correct creation of ElementId
        eid = ElementId(view_id_int)
        view_elem = doc.GetElement(eid)

        if not view_elem:
            raise Exception("No view found with id {0}".format(view_id_int))

        # Switch active view
        uiapp.ActiveUIDocument.ActiveView = view_elem

        result = {
            "status": "ok",
            "opened_view_id": view_id_int,
            "opened_view_name": view_elem.Name
        }

        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

        with open(RESPONSE_PATH, "w") as f:
            json.dump(result, f, indent=2)

        log("Opened view id {0}: {1}".format(view_id_int, view_elem.Name))

    except Exception as e:
        with open(RESPONSE_PATH, "w") as f:
            json.dump({"error": str(e)}, f, indent=2)
        log("Error in open_view_by_id: {0}".format(e))
