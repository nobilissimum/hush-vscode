import os

from typing import Final

DEFAULT_THEME_MODE: Final[str] = "vs-dark"

COLOR_HEX_LENGTH: Final[int] = 9

SRC_BASE_CONFIG_PATH: Final[str] = "src/baseConfig.json"
SRC_BASE_THEME_PATH: Final[str] = "src/baseThemes.json"

SRC_THEMES_DIRPATH: Final[str] = "src/themes"

DIST_THEMES_DIRPATH: Final[str] = "themes"

COMMANDS_DIRECTORY: Final[str] = "utils/commands"

INDENTATION: Final[int] = 2

LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "WARNING")

THEME_NAME: Final[str] = "Hush"
THEME_FILE_EXTENSION: Final[str] = "-color-theme.json"

HIDDEN_COLORS_PATH: Final[str] = "colors.hidden.json"

DEV_DIRPATH: Final[str] = "utils"

NODE_PACKAGE_PATH: Final[str] = "package.json"
