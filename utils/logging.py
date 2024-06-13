import logging
import logging.config

from logging import Formatter, LogRecord
from typing import Any

from utils.settings import LOG_LEVEL

max_level_length: int = max(
    len(f"[{level}]") for level in logging._nameToLevel  # noqa: SLF001
)


class CustomFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        record.levelname = f"[{record.levelname}]".ljust(max_level_length)
        return super().format(record)


logging_config: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL,
            "formatter": "custom",
            "stream": "ext://sys.stdout",
        },
    },
    "formatters": {
        "custom": {
            "()": CustomFormatter,
            "format": "%(asctime)s %(levelname)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S%z",
        },
    },
    "root": {
        "level": LOG_LEVEL,
        "handlers": ["console"],
    },
}


def setup_logging() -> None:
    logging.config.dictConfig(logging_config)
