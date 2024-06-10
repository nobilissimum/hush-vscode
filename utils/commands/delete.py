from os import scandir
from pathlib import Path

from utils.const import DIST_THEMES_DIRPATH


def main() -> None:
    with scandir(DIST_THEMES_DIRPATH) as directory_entries:
        for entry in directory_entries:
            Path(entry).unlink()


if __name__ == "__main__":
    main()
