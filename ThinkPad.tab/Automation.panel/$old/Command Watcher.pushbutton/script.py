# -*- coding: utf-8 -*-
import os
from pyrevit import forms
from Autodesk.Revit.UI import ExternalEvent

from CommandWatcherHelper import CommandWatcherHandler


__title__ = "👀 Command Watcher"
__doc__ = "Background watcher for file modifications using ExternalEvent."

WATCH_PATH = r"C:\PADApps\RevitPAD\Bridge\revit_command.json"


def main():
    if not os.path.exists(WATCH_PATH):
        folder = os.path.dirname(WATCH_PATH)
        if not os.path.exists(folder):
            os.makedirs(folder)
        open(WATCH_PATH, "w").close()

    handler = CommandWatcherHandler(WATCH_PATH)
    ext_event = ExternalEvent.Create(handler)

    handler.start(ext_event)

    forms.alert(
        "👀 Command Watcher started.\n\n"
        "Watching for file edits at:\n\n{0}\n\n"
        "Logs will be written to:\n{1}\n\n"
        "Close Revit to stop the watcher.".format(
            WATCH_PATH, handler.log_path
        ),
        title="Command Watcher",
    )


if __name__ == "__main__":
    main()
