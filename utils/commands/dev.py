import logging

from time import sleep, time

from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from utils.commands.build import main as build_main
from utils.settings import DEBOUNCE_INTERVAL, DEV_DIRPATH, SRC_CONFIG_DIRPATH

logger = logging.getLogger(__name__)


WATCH_DIRS = (SRC_CONFIG_DIRPATH, DEV_DIRPATH)


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback: callable) -> None:
        self.events_time = {}
        self.callback = callback

    def should_process_event(self, event: FileModifiedEvent) -> bool:
        current_time: float = time()
        event_time: str | None = self.events_time.get(event.src_path)

        if (not event_time) or ((current_time - event_time) > DEBOUNCE_INTERVAL):
            self.events_time[event.src_path] = current_time
            return True

        return False

    def on_modified(self, event: FileModifiedEvent) -> None:
        if event.is_directory or not self.should_process_event(event):
            return

        logger.info("File modified: %a", event.src_path)
        self.callback()

    def on_created(self, event: FileModifiedEvent) -> None:
        if event.is_directory or not self.should_process_event(event):
            return

        logger.info("File created: %a", event.src_path)
        self.callback()

    def on_deleted(self, event: FileModifiedEvent) -> None:
        if event.is_directory or not self.should_process_event(event):
            return

        logger.info("File deleted: %a", event.src_path)
        self.callback()


def main() -> None:
    event_handler = FileChangeHandler(build_main)
    observer = Observer()

    for directory in WATCH_DIRS:
        observer.schedule(event_handler, path=directory, recursive=True)

    observer.start()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
