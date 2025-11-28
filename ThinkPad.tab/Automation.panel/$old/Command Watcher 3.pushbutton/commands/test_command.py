
import time
from pyrevit import forms
from Autodesk.Revit.UI import TaskDialog



def log(msg):
    log_file_path = r"C:\PADApps\RevitPAD\Bridge\revit_command_log.txt"
    try:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file_path, "ab") as f:
            f.write(u"[{0}] {1}\n".format(ts, msg).encode("utf-8", "replace"))
    except Exception:
        pass


def run(uiapp, data, log):
    try:
        log("Running TEST COMMAND")
        TaskDialog.Show("Test Command", "Test command executed successfully.")  
        log("Test command completed.")
    except Exception as e:
        log("Test command error: {0}".format(e))