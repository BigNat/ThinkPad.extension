# -*- coding: utf-8 -*-
import os
import time
import json
import threading
from pyrevit import forms
from Autodesk.Revit.UI import ExternalEvent

from dispatch_command import CommandDispatcher
from watcher_state import WatcherState

REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
BRIDGE_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Bridge")
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
LOG_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Logs")

WATCH_PATH = os.path.join(BRIDGE_FOLDER, "revit_command.json")
RESULT_PATH = os.path.join(BRIDGE_FOLDER, "revit_result.json")
LOG_PATH = os.path.join(LOG_FOLDER, "revit_pad_log.txt")

def ensure_files():
    folder = os.path.dirname(WATCH_PATH)
    if not os.path.exists(folder):
        os.makedirs(folder)

    if not os.path.exists(WATCH_PATH):
        open(WATCH_PATH, "w").write("{}")

    if not os.path.exists(RESULT_PATH):
        open(RESULT_PATH, "w").write("{}")


def start_watcher(dispatcher, ext_event):
    time.sleep(1)
    dispatcher.log("Watcher loop started.")

    while WatcherState.running:
        try:
            ext_event.Raise()
        except Exception as e:
            dispatcher.log("Raise() error: {0}".format(e))

        time.sleep(0.5)



def main():
    ensure_files()

    dispatcher = CommandDispatcher(
        watch_path=WATCH_PATH, 
        log_path=LOG_PATH, 
        result_path=RESULT_PATH
        )
    
    ext_event = ExternalEvent.Create(dispatcher)

    WatcherState.running = True

    t = threading.Thread(target=start_watcher, args=(dispatcher, ext_event))
    t.daemon = True
    t.start()

    forms.alert(
        "Revit–BlueTree link established.\n\n"
        "Watcher is running.\n"
        "BlueTree may now send commands.",
        title="Command Link Active"
    )


if __name__ == "__main__":
    main()
