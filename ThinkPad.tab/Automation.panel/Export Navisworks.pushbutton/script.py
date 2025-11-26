# -*- coding: utf-8 -*-
from pyrevit import forms, revit, DB
import os, json

__title__ = "📤 Navisworks Export"
__doc__ = "Exports the current active view (with linked files) to Navisworks using global export settings."

def get_global_config_path():
    base_dir = os.path.join(os.environ["APPDATA"], "ThinkPad_Global")
    return os.path.join(base_dir, "navisworks_export_config.json")

def read_config():
    conf_path = get_global_config_path()
    if os.path.exists(conf_path):
        with open(conf_path, "r") as f:
            return json.load(f)
    return {}

def main():
    try:
        # 🔧 Load global export config
        config = read_config()
        export_dir = config.get("export_path", "").replace("\\", "/")
        export_name = config.get("name", "").strip()

        if not export_dir:
            forms.alert("⚠️ Export folder not set.\nPlease run 'Save Export Settings' first.", title="Navisworks Export")
            return

        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

        doc = revit.doc
        view = doc.ActiveView
        view_name = view.Name

        if not export_name:
            export_name = view_name.replace(":", "_").replace("\\", "_").replace("/", "_")

        safe_name = export_name.replace(":", "_").replace("\\", "_").replace("/", "_")
        export_path = os.path.join(export_dir, safe_name + ".nwc")

        # ⚙️ Navisworks export options
        options = DB.NavisworksExportOptions()
        options.ExportScope = DB.NavisworksExportScope.View
        options.ViewId = view.Id
        options.Coordinates = DB.NavisworksCoordinates.Shared

        try:
            options.ExportLinks = True
        except:
            pass

        # 🚀 Export current view
        doc.Export(export_dir, safe_name + ".nwc", options)

        forms.alert(
            "✅ Exported current view to Navisworks!\n\nView: {0}\nFile: {1}".format(view_name, export_path),
            title="Navisworks Export"
        )

    except Exception as e:
        forms.alert("❌ Export failed:\n{0}".format(e), title="Navisworks Export")

if __name__ == "__main__":
    main()
