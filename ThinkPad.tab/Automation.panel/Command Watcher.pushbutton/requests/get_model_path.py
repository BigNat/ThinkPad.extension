# -*- coding: utf-8 -*-
import os, json
from Autodesk.Revit.DB import ModelPathUtils

DATA_FOLDER = r"C:\PADApps\RevitPAD\Data"
RESPONSE = os.path.join(DATA_FOLDER, "response.json")

def run(uiapp, data, log):
    try:
        doc = uiapp.ActiveUIDocument.Document

        # Get absolute model path
        model_path = doc.PathName

        # Detect parent folder
        parent = os.path.dirname(model_path) if model_path else ""

        result = {
            "model_path": model_path,
            "parent_folder": parent,
        }

        # Persist response
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

        with open(RESPONSE, "w") as f:
            json.dump(result, f, indent=2)

        log("Returned model path → {0}".format(model_path))

    except Exception as e:
        log("Error in get_model_path: {0}".format(e))
