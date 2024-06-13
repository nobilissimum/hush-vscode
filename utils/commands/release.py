import json

from os import scandir
from pathlib import Path

from utils.settings import (
    DEFAULT_THEME_MODE,
    DIST_THEMES_DIRPATH,
    NODE_PACKAGE_PATH,
    THEME_FILE_EXTENSION,
)


def main() -> None:
    package_config: dict
    with Path(NODE_PACKAGE_PATH).open() as f:
        package_config = json.loads(f.read())

    themes: list[dict] = [
        {
            "label": theme_entry.name.replace(THEME_FILE_EXTENSION, ""),
            "uiTheme": DEFAULT_THEME_MODE,
            "path": str(Path(DIST_THEMES_DIRPATH) / Path(theme_entry.name)),
        }
        for theme_entry in sorted(
            scandir(DIST_THEMES_DIRPATH),
            key=lambda x: x.name.casefold(),
        )
    ]

    package_contributes = package_config["contributes"]
    package_contributes["themes"] = themes
    package_config["contributes"] = package_contributes

    with Path(NODE_PACKAGE_PATH).open("w") as f:
        f.write(json.dumps(package_config, indent=2))


if __name__ == "__main__":
    main()
