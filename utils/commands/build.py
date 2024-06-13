import json

from os import scandir
from pathlib import Path
from typing import Any

from utils.settings import (
    COLOR_HEX_LENGTH,
    DIST_THEMES_DIRPATH,
    INDENTATION,
    SRC_BASE_CONFIG_PATH,
    SRC_BASE_THEME_PATH,
    SRC_THEMES_DIRPATH,
    THEME_FILE_EXTENSION,
    THEME_NAME,
)


def create_theme_file(
    theme: dict,
    config: dict,
    name: str,
) -> dict:
    theme_colors = {}
    theme_token_colors = []

    # Handle `colors`
    colors: list[dict[str, str | list[str]]] = config["colors"]
    for color in colors:
        color_name = color["name"]
        color_alpha = color.get("alpha", "ff")
        color_hex = f"{theme[color_name]}{color_alpha}"[:COLOR_HEX_LENGTH].upper()

        for color_scope in color["scopes"]:
            theme_colors[color_scope] = color_hex

    # Handle `tokenColors`
    token_colors: dict[str, list[dict[str, str | list[str]]]] = config["tokenColors"]
    for color_name, color_config_groups in token_colors.items():
        base_color_hex: str = theme[color_name]

        for color_config_group in color_config_groups:
            token_color = {}
            settings = {}

            config_group_scope = color_config_group["scope"]
            config_group_scope.sort()
            token_color["scope"] = config_group_scope

            color_alpha = color_config_group.get("alpha", "ff")
            color_hex = f"{base_color_hex}{color_alpha}"[:COLOR_HEX_LENGTH].upper()
            settings["foreground"] = color_hex

            font_style = color_config_group.get("fontStyle")
            if font_style:
                settings["fontStyle"] = font_style

            token_color["settings"] = settings
            theme_token_colors.append(token_color)

    theme_file_content: dict[str, Any] = {}
    theme_file_content["colors"] = dict(sorted(theme_colors.items()))
    theme_file_content["tokenColors"] = theme_token_colors

    dist_theme_dirpath: Path = Path(DIST_THEMES_DIRPATH)
    dist_theme_dirpath.mkdir(exist_ok=True)
    with Path(f"{dist_theme_dirpath / name}{THEME_FILE_EXTENSION}").open("w") as file:
        file.write(json.dumps(theme_file_content, indent=INDENTATION))

    return theme


def create_variant_theme(base_theme: dict, variant_path: Path | str) -> dict:
    if isinstance(variant_path, str):
        variant_path = Path(variant_path)

    variant_theme: dict = base_theme.copy()
    with variant_path.open() as file:
        variant_sub_theme: dict = json.loads(file.read())
        for color_name, color_value in variant_sub_theme.items():
            variant_theme[color_name] = color_value

    return variant_theme


def main() -> None:
    theme_name: str = THEME_NAME

    base_theme: dict
    with Path(SRC_BASE_THEME_PATH).open() as file:
        base_theme = json.loads(file.read())

    base_config: dict
    with Path(SRC_BASE_CONFIG_PATH).open() as file:
        base_config = json.loads(file.read())

    # Create base theme
    create_theme_file(
        base_theme,
        base_config,
        theme_name,
    )

    # Create variant themes
    with scandir(SRC_THEMES_DIRPATH) as directory_entries:
        for entry in directory_entries:
            if not entry.is_file():
                continue

            variant_path: Path = Path(entry)
            if variant_path.suffix != ".json":
                continue

            variant_theme: dict = create_variant_theme(base_theme, variant_path)

            create_theme_file(
                variant_theme,
                base_config,
                f"{THEME_NAME} {variant_path.stem}",
            )


if __name__ == "__main__":
    main()
