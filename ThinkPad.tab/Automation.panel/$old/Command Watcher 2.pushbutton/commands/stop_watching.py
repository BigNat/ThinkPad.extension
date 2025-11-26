def run(uiapp, data, log):
    from watcher_state import WatcherState
    WatcherState.running = False
    log("Watcher stopped.")
    return {"status": "watcher_stopped"}
