import sys
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.validator import PathValidator
from rich import print as rprint
from wrapperComponents import WrapperComponents as wp
import os
from typing import Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
THEMES_DIR = os.path.join(BASE_DIR, "themes")
THEME = os.path.join(THEMES_DIR, "inquirer.json")


def read_file(file_path: str) -> str:
    """
    Reads a file and returns a list of lines.
    :param file_path: The path to the file.
    :return: A list of lines.
    """
    with open(file_path, "r") as file:
        return file.read()


def make_choices(options: list[tuple[str, Any]] | None) -> list[Choice]:
    """
    Makes a list of choices for the menu.
    :param options: The options to make choices from.
    :return: A list of choices.
    """
    choices: list[Choice] = []
    if options:
        for option in options:
            choices.append(Choice(name=option[0], value=option[1]))
    return choices



def menu(
    title: str, mode="select", options: list[tuple[str, Any]] | None = None, base_path=None
):
    """
    A simple menu for the user to choose from.
    :param title: The title of the menu.
    :param mode: The type of menu to use.
    :param options: The options the user can choose from.
    :param base_path: The base path to use for the file menu.
    :return: The option the user chose.
    """
    # inquirer.themes.load_theme_from_json(read_file(THEME))
    if mode == "select":
        ch = make_choices(options)
    try:
        if mode == "select":
            res = inquirer.select(
                message=title,
                choices=ch,
                default=None,
            ).execute()
        elif mode == "file":
            home_path = os.getcwd() if base_path is None else base_path
            res = inquirer.filepath(
                message=title,
                default=home_path,
                validate=PathValidator(is_file=True, message="Input is not a file"),
                only_files=True,
            ).execute()

    except Exception as e:
        rprint(f"{wp.textWrapBold('An error occured: ', 'red')}{wp.textWrap(str(e), 'red')}")
        rprint(f"{wp.textWrapBold('Exiting program...', 'red')}")
        sys.exit(1)
    return res


if __name__ == "__main__":
    MODE = menu(
        "Choose the mode you want to use:",
        "select",
        [("Watch and Run Self (WRS)", "wrs"), ("Watch and Run Other (WRO)", "wro")],
    )
    PATH = menu(
        "Choose the file you want to watch and run:",
        "file",
    )
    print(MODE)
    print(PATH)
