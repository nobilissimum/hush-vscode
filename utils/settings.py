import os

from typing import Final

SRC_CONFIG_DIRPATH: Final[str] = "src"
DEV_DIRPATH: Final[str] = "utils"

DEFAULT_THEME_MODE: Final[str] = "vs-dark"

COLOR_HEX_LENGTH: Final[int] = 9

SRC_VARIANT_THEMES_DIR: Final[str] = "variants"
SRC_BASE_CONFIG_FILENAME: Final[str] = "config.json"
SRC_BASE_COLORS_FILENAME: Final[str] = "colors.json"

DIST_THEMES_DIRPATH: Final[str] = "themes"

COMMANDS_DIRECTORY: Final[str] = "utils/commands"

INDENTATION: Final[int] = 2

LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "WARNING")
DEBOUNCE_INTERVAL: float = 1

THEME_NAME: Final[str] = "Hush"
THEME_FILE_EXTENSION: Final[str] = ".json"

HIDDEN_COLORS_PATH: Final[str] = "colors.hidden.json"

NODE_PACKAGE_PATH: Final[str] = "package.json"
