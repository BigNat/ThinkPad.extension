def run(uiapp, data, log):
    from watcher_state import WatcherState
    WatcherState.running = True
    log("Watcher started.")
    return {"status": "watcher_started"}
