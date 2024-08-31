import json

from enum import Enum
from functools import cmp_to_key
from os import DirEntry, scandir
from pathlib import Path

from utils.settings import (
    DIST_THEMES_DIRPATH,
    NODE_PACKAGE_PATH,
)


class Release(Enum):
    MAJOR = 0
    MINOR = 1
    PATCH = 2

    def __str__(self) -> str:
        return str(self.value)


def get_stem_and_suffixes(
    path: Path,
    *,
    is_casefold: bool = True,
) -> tuple[str, bool]:
    suffixes: list[str] = path.suffixes
    stem: str = path.name.removesuffix("".join(suffixes))

    if is_casefold:
        stem = stem.casefold()

    return stem, ".light" in suffixes


def sort_themes(entry_a: DirEntry, entry_b: DirEntry) -> str:
    name_a, is_light_a = get_stem_and_suffixes(Path(entry_a))
    name_b, is_light_b = get_stem_and_suffixes(Path(entry_b))

    if is_light_a and (not is_light_b):
        return 1

    if (not is_light_a) and is_light_b:
        return -1

    return 1 if name_a > name_b else -1


def increase_version(package_config: dict, release: Release) -> dict:
    revisions: list[int] = [
        int(revision) for revision in package_config["version"].split(".")
    ]
    revisions[release.value] = revisions[release.value] + 1
    package_config["version"] = ".".join(str(revision) for revision in revisions)

    return package_config


def main(release: str = Release.MINOR.name.lower()) -> None:
    package_config: dict
    with Path(NODE_PACKAGE_PATH).open() as f:
        package_config = json.loads(f.read())

    themes: list[dict] = []
    for theme_entry in sorted(
        scandir(DIST_THEMES_DIRPATH),
        key=cmp_to_key(sort_themes),
    ):
        theme_suffixes: list[str] = Path(theme_entry).suffixes
        ui_theme: str = "vs" if ".light" in theme_suffixes else "vs-dark"
        themes.append(
            {
                "label": theme_entry.name.removesuffix("".join(theme_suffixes)),
                "uiTheme": ui_theme,
                "path": str(Path(DIST_THEMES_DIRPATH) / Path(theme_entry.name)),
            },
        )

    package_contributes = package_config["contributes"]
    package_contributes["themes"] = themes
    package_config["contributes"] = package_contributes

    package_config = increase_version(
        package_config,
        getattr(Release, release.upper(), Release.MINOR.name),
    )
    with Path(NODE_PACKAGE_PATH).open("w") as f:
        f.write(json.dumps(package_config, indent=2))


if __name__ == "__main__":
    main()
