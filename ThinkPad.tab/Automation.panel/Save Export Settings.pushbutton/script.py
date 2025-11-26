# -*- coding: utf-8 -*-
from pyrevit import forms
import os, json

__title__ = "💾 Export Settings"
__doc__ = "Reads and saves Navisworks export settings to a global JSON file."

def get_global_config_path():
    base_dir = os.path.join(os.environ["APPDATA"], "ThinkPad_Global")
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    return os.path.join(base_dir, "navisworks_export_config.json")

def read_config():
    conf_path = get_global_config_path()
    if os.path.exists(conf_path):
        with open(conf_path, "r") as f:
            return json.load(f)
    return {}

def write_config(data):
    conf_path = get_global_config_path()
    with open(conf_path, "w") as f:
        json.dump(data, f, indent=4)
    return conf_path

def main():
    # Load current settings
    config = read_config()
    current_name = config.get("name", "")
    current_export_path = config.get("export_path", "")

    # Ask for export name
    name = forms.ask_for_string(
        default=current_name, prompt="Enter export name:", title="Navisworks Export Config"
    )
    if not name:
        return

    # Ask for folder
    export_path = forms.pick_folder(title="Select Export Folder")
    if not export_path:
        return

    # Save config
    new_config = {
        "name": name,
        "export_path": export_path.replace("\\", "/")
    }
    conf_path = write_config(new_config)

    msg = (
        "✅ Export settings saved!\n\n"
        "📄 Name: {0}\n"
        "📁 Path: {1}\n\n"
        "Config stored at:\n{2}"
    ).format(name, export_path, conf_path)

    forms.alert(msg, title="Global Export Config")

if __name__ == "__main__":
    main()
