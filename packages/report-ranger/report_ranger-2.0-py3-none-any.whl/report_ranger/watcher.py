import logging
from watchdog.events import FileSystemEventHandler
import pathlib
import time

log = logging.getLogger(__name__)

class Watcher(FileSystemEventHandler):
    def __init__(self, callback=None, *args, **kwargs):
        FileSystemEventHandler.__init__(self)
        self.paths = []
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.to_run = False
        self.watch_mode = ''
        self.prevtime = time.time()
        self.running = False
    
    def set_callback(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
    
    def set_running(self):
        self.running = True

    def stop_running(self):
        self.running = False

    def set_watch_mode(self, watch_mode):
        self.watch_mode = watch_mode

    def add_path(self, path):
        self.paths.append(pathlib.Path(path))
        log.info(f"Added {path} to watch paths")
    
    def clear_paths(self):
        self.paths.clear()

    def in_paths(self, path):
        return pathlib.Path(path) in self.paths

    def on_moved(self, event):
        log.info(f"Moved: {event.src_path()} in {self.paths}")
        if self.in_paths(event.dest_path()) or self.in_paths(event.src_path()):
            self.to_run = True
    
    def on_modified(self, event):
        log.info(f"Modified: {event.src_path()} in {self.paths}")
        if self.in_paths(event.src_path()):
            self.to_run = True

    def on_deleted(self, event):
        log.info(f"Deleted: {event.src_path()} in {self.paths}")
        if self.in_paths(event.src_path()):
            self.to_run = True

    def run(self):
        if self.running:
            log.info("Still running, skipping recompile")
            return
        if self.watch_mode == "modified":
            for path in self.paths:
                if path.is_dir():
                    for df in [pth for pth in pathlib.Path(path).iterdir() if pth.suffix == '.md']:
                        mtime = df.stat().st_mtime
                        if self.prevtime < df.stat().st_mtime or self.prevtime < df.stat().st_ctime:
                            self.to_run = True
                            break
                elif path.is_file():
                    mtime = path.stat().st_mtime
                    if self.prevtime < mtime:
                        self.to_run = True
                        break
                else:
                    self.to_run = True
            
            self.prevtime = time.time()
        if self.to_run == True:
            self.callback(*self.args, **self.kwargs)
            self.to_run = False
        else:
            log.info(f"No modifications found")
    
    
