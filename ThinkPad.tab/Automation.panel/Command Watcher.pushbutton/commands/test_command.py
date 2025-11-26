
from Autodesk.Revit.UI import TaskDialog

def run(uiapp, data, log):
    try:
        log("Running TEST COMMAND")
        TaskDialog.Show("Test Command", "Test command executed successfully.")  
        log("Test command completed.")
    except Exception as e:
        log("Test command error: {0}".format(e))