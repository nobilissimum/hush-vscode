import json
import logging

from logging import Logger
from pathlib import Path

from utils.const import HIDDEN_COLORS_PATH, INDENTATION, SRC_BASE_CONFIG_PATH

logger: Logger = logging.getLogger()


def main() -> list:
    config: dict
    with Path(SRC_BASE_CONFIG_PATH).open() as file:
        config = json.loads(file.read())

    colors: list = []
    colors.extend(color for color in config.get("colors", {}) if color not in colors)
    colors.extend(
        color for color in config.get("tokenColors", {}) if color not in colors
    )

    with Path(HIDDEN_COLORS_PATH).open("w+") as file:
        file.write(json.dumps(colors, indent=INDENTATION))
        logger.info("Created file %a", HIDDEN_COLORS_PATH)

    return colors


if __name__ == "__main__":
    main()
