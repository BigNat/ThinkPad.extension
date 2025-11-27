# -*- coding: utf-8 -*-
import os
import sys
import time
import threading
import json
import importlib
from pyrevit import forms
from Autodesk.Revit.UI import IExternalEventHandler

REVIT_PAD_FOLDER = r"C:\PADApps\RevitPAD"
BRIDGE_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Bridge")
DATA_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Data")
LOG_FOLDER = os.path.join(REVIT_PAD_FOLDER, "Logs")

class CommandWatcherHandler(IExternalEventHandler):
    """Revit command dispatcher that dynamically loads command modules."""

    def __init__(self, watch_path):
        self.uiapp_cached = None 
        self.event_pending = False
        self.watch_path = watch_path
        self.last_mod_time = None
        self.last_command = None


        self.keep_running = True
        base_dir = os.path.dirname(watch_path)
        self.commands_dir = os.path.join(os.path.dirname(__file__), "commands")
        self.requests_dir = os.path.join(os.path.dirname(__file__), "requests")




        self.log_path = os.path.join(LOG_FOLDER, "revit_pad_log.txt")

        # Ensure commands directory is in import path
        if self.commands_dir not in sys.path:
            sys.path.append(self.commands_dir)

    def log(self, msg):
        try:
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_path, "ab") as f:
                f.write(u"[{0}] {1}\n".format(ts, msg).encode("utf-8", "replace"))
        except Exception:
            pass

    def Execute(self, uiapp):

        try:
            if not os.path.exists(self.watch_path):
                return
            
            if os.path.getsize(self.watch_path) < 5:
                return
                
            if self.uiapp_cached is None:
                self.uiapp_cached = uiapp
                self.log("Cached UIApplication")

            mod_time = os.path.getmtime(self.watch_path)
            if mod_time == self.last_mod_time:
                return
            self.last_mod_time = mod_time

            # --- wait for writer to finish ---
            for _ in range(10):
                if os.path.getsize(self.watch_path) > 5:
                    break
                time.sleep(0.05)

            

            with open(self.watch_path, "r") as f:
                data = json.load(f)

            cmd = (data.get("command") or data.get("request") or "").strip()
            if not cmd or cmd == self.last_command:
                return

            self.last_command = cmd
            self.log("Command received: {0}".format(cmd))
            self.run_command(cmd, uiapp, data)

        except Exception as e:
            self.log("Error in Execute: {0}".format(e))

        finally:
            self.event_pending = False


    def run_command(self, cmd, uiapp, data):
        

        try:
            if cmd == "stop_watcher":
                self.log("Received stop_watcher command. Stopping loop.")

                # Remove the lock file
                try:
                    os.remove(os.path.join(BRIDGE_FOLDER, "watcher.lock"))
                    self.log("Watcher lock file removed.")
                except:
                    pass

                # Clear the command file to prevent reprocessing
                try:
                    with open(self.watch_path, "w") as f:
                        f.write("{}")
                    self.log("stop_watcher cleared from JSON file.")
                except:
                    self.log("Failed to clear stop_watcher from JSON file.")

                # Reset last command so nothing lingers
                self.last_command = None

                # Stop the loop
                self.keep_running = False
                return


            module_name = cmd.replace("-", "_")

            if "request" in data:
                module_path = self.requests_dir
            else:
                module_path = self.commands_dir

            sys.path.append(module_path)

            self.log("IMPORTING: {0}".format(module_name))
            module = importlib.import_module(module_name)

            self.log("LOADED FROM: {0}".format(getattr(module, "__file__", "UNKNOWN")))

            # IronPython reload (Python 2 syntax)
            try:
                reload(module)
            except Exception as e:
                self.log("Reload warning: {0}".format(e))

            if hasattr(module, "run"):
                data["watch_path"] = self.watch_path
                module.run(uiapp, data, self.log)

                # NEW: clear file to stop repeats
                try:
                    with open(self.watch_path, "w") as f:
                        f.write("{}")
                    self.log("Command cleared from JSON file.")
                except:
                    self.log("Failed to clear command file.")

                self.last_command = None

        except Exception as e:
            self.log("⚠ Command failed ({0}): {1}".format(cmd, e))
            forms.alert("⚠ Command failed:\n{0}\n\n{1}".format(cmd, e),
                        title="Command Watcher")


    def GetName(self):
        return "Command Watcher Event"

    def start(self, ext_event, interval=3):

        def loop():
            time.sleep(5)
            self.log("Command Watcher active.")

            while True:
                if not self.keep_running:
                    self.log("Watcher loop exiting cleanly.")
                    return  # <-- EXIT THREAD IMMEDIATELY

                # HEARTBEAT
                try:
                    heartbeat_path = os.path.join(BRIDGE_FOLDER, "revit_heartbeat.json")
                    with open(heartbeat_path, "w") as hb:
                        hb.write(json.dumps({"timestamp": time.time(), "status": "alive"}))
                except:
                    pass

                # Raise events
                if not self.event_pending:
                    self.event_pending = True
                    try:
                        ext_event.Raise()
                    except:
                        self.event_pending = False

                # Short sleep for responsive shutdown
                for _ in range(30):   # 30 × 0.1s = 3 seconds total
                    if not self.keep_running:
                        self.log("Watcher loop stopping during sleep.")
                        return
                    time.sleep(0.1)


        t = threading.Thread(target=loop)
        t.daemon = True
        t.start()
