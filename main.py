import importlib
import importlib.util
import logging
import os

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import TYPE_CHECKING

from dotenv import load_dotenv

from utils.logging import setup_logging
from utils.settings import COMMANDS_DIRECTORY

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec
    from types import ModuleType

load_dotenv()
setup_logging()

logger = logging.getLogger()


def parse_args() -> Namespace:
    parser: ArgumentParser = ArgumentParser(description="Run a command script.")
    parser.add_argument("script_name", type=str, help="The name of the script to run")
    parser.add_argument(
        "script_args",
        nargs="*",
        help="Arguments to pass to the script",
    )
    return parser.parse_args()


def find_script(script_name: str) -> str | None:
    folder: str = COMMANDS_DIRECTORY
    scripts = [
        file
        for file in os.listdir(folder)
        if file.endswith(".py") and not file.startswith("__init__")
    ]
    for script in scripts:
        script_path = Path(script)
        if script_name == script_path.stem:
            return Path(folder) / script_path

    return None


def run_script(script_path: str | Path, script_args: list[str]) -> None:
    if isinstance(script_path, str):
        script_path: Path = Path(script_path)

    script_name = script_path.stem
    spec: ModuleSpec = importlib.util.spec_from_file_location(script_name, script_path)
    module: ModuleType = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "main"):
        logger.error("Script `%a` does not have a main function.", script_path)

    module.main(*script_args)


def main() -> None:
    args: Namespace = parse_args()
    script_path: str | None = find_script(args.script_name)

    if not script_path:
        logger.error(
            "Script `%a` not found",
            args.script_name,
        )
        return

    logger.info("Running script: %a with args: %a", script_path, args.script_args)
    run_script(script_path, args.script_args)
    return


if __name__ == "__main__":
    main()
