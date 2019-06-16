import time
from cprint import cprint
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from pyp5js.compiler import compile_sketch_js



def monitor_sketch(sketch_files):
    observer = Observer()

    event_handler = TranscryptSketchEventHandler(sketch_files=sketch_files, observer=observer)

    observer.schedule(event_handler, sketch_files.sketch_dir)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt as e:
        observer.stop()
        raise e
    observer.join()


class TranscryptSketchEventHandler(PatternMatchingEventHandler):
    patterns = ["*.py"]

    def __init__(self, *args, **kwargs):
        self.sketch_files = kwargs.pop('sketch_files')
        self.observer = kwargs.pop('observer')
        self._last_event = None
        super().__init__(*args, **kwargs)

    def on_modified(self, event):
        cprint.info(f"New change in {event.src_path}")

        # monkey patch on the observer handlers to avoid recursion
        handlers_config = self.observer._handlers.copy()
        handlers_copy = {}

        compile_sketch_js(self.sketch_files)

        queue = self.observer.event_queue
        while queue.qsize():
            queue.get()

        index_file = self.sketch_files.index_html
        cprint.ok(f"Your sketch is ready and available at file://{index_file.absolute()}")
