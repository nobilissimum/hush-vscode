import json

from enum import Enum
from os import scandir
from pathlib import Path
from re import Pattern, compile
from typing import Any, Final, Self

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

BASE_COLOR_PATTERN: Pattern = compile(r"^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$")
ALPHA_COLOR_PATTERN: Pattern = compile(r"^[A-Fa-f0-9]{2}")

HEX_LENGTH: Final[int] = 2
RGB_HEX_LENGTH: Final[int] = 6

HEX_BASE: Final[int] = 16
HEX_MAX: Final[int] = 255


class UiTheme(Enum):
    LIGHT = "light"
    DARK = "dark"

    def __str__(self) -> str:
        return self.value


class Color:
    base: str
    alpha: str

    base_alpha: float
    extra: str

    def __init__(
        self,
        base: str,
        alpha: str = "",
        base_alpha: str = "",
        extra: str = "",
    ) -> None:
        if not BASE_COLOR_PATTERN.match(base):
            error_message: str = "The base color should be hexadecimal"
            raise AssertionError(error_message)

        base = base[: RGB_HEX_LENGTH + 1]
        alpha = alpha[:HEX_LENGTH]
        extra, base_alpha = self.validate_extra(extra, base_alpha)

        self.base = base
        self.alpha = alpha
        self.base_alpha = base_alpha
        self.extra = extra

    def __str__(self) -> str:
        return self.value

    def validate_alpha(self, alpha: str) -> str:
        if not alpha:
            return alpha

        if not ALPHA_COLOR_PATTERN.match(alpha):
            error_message: str = "The alpha should be hexadecimal"
            raise AssertionError(error_message)

        return alpha[:HEX_LENGTH]

    def validate_extra(self, extra: str, base_alpha: str) -> tuple[str, str]:
        if not extra:
            return extra, base_alpha

        extra = extra[: RGB_HEX_LENGTH + 1]
        if not BASE_COLOR_PATTERN.match(extra):
            error_message: str = "The extra color should be hexadecimal"
            raise AssertionError(error_message)

        base_alpha = base_alpha[:HEX_LENGTH]
        if not ALPHA_COLOR_PATTERN.match(base_alpha):
            error_message: str = "The base alpha should be hexadecimal"
            raise AssertionError(error_message)

        return extra, base_alpha

    @property
    def value(self) -> str:
        if not self.extra:
            return f"{self.base}{self.alpha}"

        base_hex: str = self.base[1:]
        bases: tuple[int, int, int] = tuple(
            int(self.base[1:][i : i + HEX_LENGTH], HEX_BASE)
            for i in range(0, len(base_hex), HEX_LENGTH)
        )

        extra_hex: str = self.extra[1:]

        base_alpha_hex: int = int(self.base_alpha, HEX_BASE)
        base_alpha: int = base_alpha_hex / HEX_MAX
        extra_alpha: int = (HEX_MAX - base_alpha_hex) / HEX_MAX

        extras: tuple[int, int, int] = tuple(
            int(self.extra[1:][i : i + HEX_LENGTH], HEX_BASE) * extra_alpha
            for i in range(0, len(extra_hex), HEX_LENGTH)
        )

        bases = tuple(
            hex(round((base - extras[index]) / base_alpha))[2:]
            for index, base in enumerate(bases)
        )
        return f"#{''.join(bases)}{self.base_alpha}".lower()


class Theme:
    theme_colors: dict
    theme_config: dict

    variant_name: str
    ui_theme: UiTheme
    colors: dict
    token_colors: dict

    def __init__(
        self,
        ui_theme: UiTheme,
        theme_colors: dict | None = None,
        theme_config: dict | None = None,
        variant_name: str = "",
    ) -> None:
        self.ui_theme = ui_theme
        self.variant_name = variant_name
        self.theme_colors = theme_colors or {}
        self.theme_config = theme_config or {}

    def set_theme_colors(self, theme_colors: dict) -> Self:
        self.theme_colors = {**self.theme_colors, **theme_colors}
        return self

    def set_theme_config(self, theme_config: dict) -> Self:
        self.theme_config = theme_config
        return self

    def build_colors(self) -> None:
        colors: dict[str, str] = {}

        for color_name, color_variants in self.theme_config["colors"].items():
            for alpha, scopes in color_variants.items():
                color: Color = Color(self.theme_colors[color_name], alpha)

                for color_scope in scopes:
                    colors[color_scope] = color.value

        self.colors = colors

    def build_token_colors(self) -> None:
        token_colors: dict = {}

        for color_name, color_config_groups in self.theme_config["tokenColors"].items():
            base_color_hex: str = self.theme_colors[color_name]

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
                token_colors.append(token_color)

        self.token_colors = token_colors

    def build(self) -> None:
        self.build_colors()
        self.build_token_colors()

    def create_file(self) -> None:
        if not self.colors:
            msg: str = (
                f"Theme  {self.variant_name}:{self.ui_theme} has no configured colors"
            )
            raise AssertionError(msg)

        if not self.token_colors:
            msg: str = (
                f"Theme  {self.variant_name}:{self.ui_theme}"
                "has no configured token colors"
            )
            raise AssertionError(msg)

        ui_theme: str = self.ui_theme.value
        theme: dict = {
            "type": ui_theme,
            "colors": self.colors,
            "tokenColors": self.token_colors,
        }

        dist_theme_dirpath: Path = Path(DIST_THEMES_DIRPATH)
        dist_theme_dirpath.mkdir(exist_ok=True)

        name: str = THEME_NAME
        if self.variant_name:
            name = f"{name.capitalize()} {self.variant_name.capitalize()}"

        with Path(
            f"{dist_theme_dirpath / name}.{ui_theme}{THEME_FILE_EXTENSION}",
        ).open("w") as file:
            file.write(json.dumps(theme, indent=INDENTATION))


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
        f"{dist_theme_dirpath / name}.{theme_type}{THEME_FILE_EXTENSION}",
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
