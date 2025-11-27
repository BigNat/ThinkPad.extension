# -*- coding: utf-8 -*-
import os
import json

REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
RESPONSE_PATH = os.path.join(DATA_FOLDER, "response.json")


def run(uiapp, data, log):
    """
    Returns information about the current active view in Revit.
    """
    try:
        doc = uiapp.ActiveUIDocument.Document
        view = doc.ActiveView

        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

        result = {
            "view_name": view.Name,
            "view_id": view.Id.IntegerValue,
            "view_type": str(view.ViewType)
        }

        with open(RESPONSE_PATH, "w") as f:
            json.dump(result, f, indent=2)

        log("Returned active view information: {0}".format(view.Name))

    except Exception as e:
        # Return error in response.json
        with open(RESPONSE_PATH, "w") as f:
            json.dump({"error": str(e)}, f, indent=2)
        log("Error in get_active_view: {0}".format(e))
