# -*- coding: utf-8 -*-
import os
import json
import time
import importlib
import sys
from pyrevit import forms
from Autodesk.Revit.UI import IExternalEventHandler

from watcher_state import WatcherState


class CommandDispatcher(IExternalEventHandler):
    """Receives ExternalEvent, reads JSON, dispatches commands, writes results."""

    def __init__(self, watch_path, log_path, result_path):
        self.watch_path = watch_path
        self.last_command = None
        self.log_path = log_path
        self.result_path = result_path
        self.commands_dir = os.path.join(os.path.dirname(__file__), "commands")

        if self.commands_dir not in sys.path:
            sys.path.append(self.commands_dir)

        self.log("=== Dispatcher initialised ===")
        self.log("WatchPath: {0}".format(self.watch_path))
        self.log("ResultPath: {0}".format(self.result_path))
        self.log("CommandsDir: {0}".format(self.commands_dir))
        self.log("================================")

    # ----------------------------------------------------------------------
    def log(self, msg):
        ts = time.strftime("%H:%M:%S")
        try:
            with open(self.log_path, "ab") as f:
                line = "[{0}] {1}\n".format(ts, msg)
                f.write(line.encode("utf-8", "replace"))
        except:
            pass

    # ----------------------------------------------------------------------
    def Execute(self, uiapp):
        """Called by Revit ExternalEvent system."""
        try:
            self.log("Execute() fired. Checking JSON...")
            if not os.path.exists(self.watch_path):
                self.log("Watch path missing. Nothing to do.")
                return

            size = os.path.getsize(self.watch_path)
            self.log("JSON file size: {0} bytes".format(size))

            # Read JSON ----------------------------------------------------------------
            try:
                with open(self.watch_path, "r") as f:
                    data = json.load(f)
                self.log("JSON read OK.")
            except Exception as e:
                self.log("ERROR reading JSON: {0}".format(e))
                return

            cmd = data.get("command", "").strip()
            self.log("Command field: '{0}'".format(cmd))

            # No command?
            if not cmd:
                self.log("No command found. Returning.")
                return

            # Same command as last time?
            if cmd == self.last_command:
                self.log("Skipping: same command as last time ('{0}').".format(cmd))
                return

            # NEW command
            self.log("NEW COMMAND detected: {0}".format(cmd))
            self.last_command = cmd

            # Dispatch it
            self.dispatch(uiapp, cmd, data)

        except Exception as e:
            self.log("Dispatcher error in Execute: {0}".format(e))

    # ----------------------------------------------------------------------
    def dispatch(self, uiapp, cmd, data):
        """Load module, call run(), write results."""
        start_ts = time.time()
        self.log("Dispatching '{0}'...".format(cmd))

        try:
            # Import -----------------------------------------------------------------
            self.log("Importing module: {0}".format(cmd))
            module = importlib.import_module(cmd)

            module_path = getattr(module, "__file__", "UNKNOWN")
            self.log("Module loaded from: {0}".format(module_path))

            # Reload -----------------------------------------------------------------
            try:
                reload(module)
                self.log("Module reloaded successfully.")
            except Exception as e:
                self.log("Module reload warning: {0}".format(e))

            # Run Command -------------------------------------------------------------
            if hasattr(module, "run"):
                self.log("Executing run() in '{0}'...".format(cmd))
                result = module.run(uiapp, data, self.log)
                self.log("run() finished.")
                self.write_result(result)
                self.log("Command completed OK: {0}".format(cmd))
            else:
                self.log("ERROR: No run() in module '{0}'".format(cmd))

        except Exception as e:
            self.log("Dispatch ERROR for '{0}': {1}".format(cmd, e))

        finally:
            # Clear JSON --------------------------------------------------------------
            try:
                with open(self.watch_path, "w") as f:
                    f.write("{}")
                self.log("Command file cleared.")
            except Exception as e:
                self.log("Failed to clear command file: {0}".format(e))

            elapsed = time.time() - start_ts
            self.log("Dispatch ended. Duration: {0:.3f}s".format(elapsed))

    # ----------------------------------------------------------------------
    def write_result(self, result):
        """Write the result JSON returned by the module."""
        try:
            self.log("Writing result to: {0}".format(self.result_path))
            with open(self.result_path, "w") as f:
                json.dump(result or {"status": "ok"}, f, indent=2)
            self.log("Result written successfully.")
        except Exception as e:
            self.log("Failed to write result file: {0}".format(e))

    # ----------------------------------------------------------------------
    def GetName(self):
        return "Command Dispatcher"
