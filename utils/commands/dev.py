import time

from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from utils.commands.build import main as build_main
from utils.const import DEV_DIRPATH
from utils.logging import logger


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback: callable) -> None:
        self.callback = callback

    def on_modified(self, event: FileModifiedEvent) -> None:
        if not event.is_directory:
            logger.info("File modified: %a", event.src_path)
            self.callback()

    def on_created(self, event: FileModifiedEvent) -> None:
        if not event.is_directory:
            logger.info("File created: %a", event.src_path)
            self.callback()

    def on_deleted(self, event: FileModifiedEvent) -> None:
        if not event.is_directory:
            logger.info("File deleted: %a", event.src_path)
            self.callback()


def main() -> None:
    event_handler = FileChangeHandler(build_main)
    observer = Observer()
    observer.schedule(event_handler, path=DEV_DIRPATH, recursive=True)
    observer.schedule(event_handler, path="src", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
