import json

from os import scandir
from pathlib import Path
from typing import Any

from utils.settings import (
    COLOR_HEX_LENGTH,
    DIST_THEMES_DIRPATH,
    INDENTATION,
    SRC_BASE_CONFIG_FILENAME,
    SRC_BASE_THEME_FILENAME,
    SRC_CONFIG_DIRPATH,
    SRC_VARIANT_THEMES_DIR,
    THEME_FILE_EXTENSION,
    THEME_NAME,
)


def get_color_hex(
    theme: dict,
    color_name: str,
    alpha: str,
) -> str | None:
    if color_name == "$":
        return None

    color_alpha: str = alpha if alpha != "$" else ""
    return f"{theme[color_name]}{color_alpha}"[:COLOR_HEX_LENGTH].upper()


def create_theme_file(
    theme: dict,
    theme_type: str,
    config: dict,
    name: str,
) -> dict:
    theme_colors = {}
    theme_token_colors = []

    # Handle `colors`
    colors: dict[str, dict[str, list[str]]] = config["colors"]
    for color_name, variants in colors.items():
        for alpha, color_scopes in variants.items():
            color_hex = get_color_hex(theme, color_name, alpha)

            for color_scope in color_scopes:
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

    theme_file_content: dict[str, Any] = {"type": theme_type}
    theme_file_content["colors"] = dict(sorted(theme_colors.items()))
    theme_file_content["tokenColors"] = theme_token_colors

    dist_theme_dirpath: Path = Path(DIST_THEMES_DIRPATH)
    dist_theme_dirpath.mkdir(exist_ok=True)
    with Path(
        f"{dist_theme_dirpath / name}"
        f".{theme_type}"
        f"{THEME_FILE_EXTENSION}",
    ).open("w") as file:
        file.write(json.dumps(theme_file_content, indent=INDENTATION))

    return theme


def create_variant_theme(base_theme: dict, variant_path: Path | str) -> dict:
    if isinstance(variant_path, str):
        variant_path = Path(variant_path)

    variant_theme: dict = base_theme.copy()
    with variant_path.open() as file:
        variant_sub_theme: dict[str, str] = json.loads(file.read())
        for color_name, color_value in variant_sub_theme.items():
            variant_theme[color_name] = color_value

    return variant_theme


def main() -> None:
    theme_name: str = THEME_NAME

    src_config_dirpath: Path = Path(SRC_CONFIG_DIRPATH)
    base_config: dict
    with Path(src_config_dirpath / SRC_BASE_CONFIG_FILENAME).open() as file:
        base_config = json.loads(file.read())

    with scandir(src_config_dirpath) as type_entries:
        for type_entry in type_entries:
            if not type_entry.is_dir():
                continue

            type_name: str = type_entry.name
            type_dirpath: Path = Path(type_entry)
            base_theme: dict = {}
            with Path(type_dirpath / SRC_BASE_THEME_FILENAME).open() as file:
                base_theme.update(json.loads(file.read()))

            # Create base theme
            create_theme_file(
                base_theme,
                type_name,
                base_config,
                theme_name,
            )

            # Create variant themes
            variants_dirpath: Path = type_dirpath / SRC_VARIANT_THEMES_DIR
            if not variants_dirpath.exists():
                continue

            with scandir(type_dirpath / SRC_VARIANT_THEMES_DIR) as directory_entries:
                for directory_entry in directory_entries:
                    if not directory_entry.is_file():
                        continue

                    variant_path: Path = Path(directory_entry)
                    if variant_path.suffix != ".json":
                        continue

                    variant_theme: dict = create_variant_theme(base_theme, variant_path)

                    create_theme_file(
                        variant_theme,
                        type_name,
                        base_config,
                        f"{THEME_NAME} {variant_path.stem}",
                    )


if __name__ == "__main__":
    main()
