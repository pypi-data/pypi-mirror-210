"""
detectchange CLI module
===
"""

import time
import os

from rich import print as rprint
from rich.console import Console
import typer

from watchdog.observers import Observer
from pyfiglet import Figlet
import tomli

import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from menu import menu
from wrapperComponents import WrapperComponents as wp
from makeParser import Parser

# handlers
from wrs import WrsHandler
from wro import WroHandler
from wtch import WatchForHandler
from wrm import WrmHandler

# Version Control
from versionControl import VersionControl
from gobals_variables import VARS as v



class Entries:
    """
    Save all the data values
    """
    def __init__(self, is_empty=False):
        self.entries = {}
        self.c = Console()
        self.is_empty = is_empty

    def add(self, name: str, value):
        """Add a new element"""
        self.entries[name] = value

    def get(self, name: str) -> str | list | None | bool | int | list[str]:
        """Get an Element"""
        return self.entries.get(name, None)

    def makeMode(self):
        """Function to get the running mode"""
        MODE = menu(
            "Choose the mode you want to use:",
            "select",
            [("Watch and Run Self (WRS)", "wrs"),
             ("Watch and Run Other (WRO)", "wro"),
             ("Makefile", "mk")],
        )
        self.add("mode", MODE)

    def makeLang(self):
        """Get the language"""
        self.language = menu(
            "Choose the language you want to use:",
            "select",
            [("python", "python"), ("ruby", "ruby"), ("c", "c"), ("c++", "c++")],
        )
        self.add("lang", self.language)

    def makeCParams(self):
        """Get C parameters"""
        wywu = wp.textWrapBold("Enter the compiler name you want to use : ")
        ccho = wp.textWrapBold("( g++ | gcc | ...) ", "green")
        CMD = self.c.input(f"{wywu}{ccho}")
        self.add("cmd", [CMD])
        opt1 = wp.textWrapBold("Enter flags you want to use : ")
        default = wp.textWrapBold("(none) ", "green")
        FLAGS = self.c.input(f"{opt1}{default}").split(" ")
        if FLAGS in ["none", "", " "]:
            FLAGS = [""]
        self.add("flags", FLAGS)
        output = wp.textWrapBold("Enter the output attributes you want to use: ")
        default = wp.textWrapBold("(-o) ", "green")
        OUTPUT_ATTRIBUTE = self.c.input(f"{output}{default}")
        if OUTPUT_ATTRIBUTE in ["", " "]:
            OUTPUT_ATTRIBUTE = "-o"
        self.add("output_attr", OUTPUT_ATTRIBUTE)
        output_name = wp.textWrapBold("Enter the output name you want: ")
        default = wp.textWrapBold("(out) ", "green")
        OUTPUT_FILE = self.c.input(f"{output_name}{default}").lower()
        if OUTPUT_FILE in ["", " "]:
            OUTPUT_FILE = "out"
        self.add("output_file", OUTPUT_FILE)

    def makeCommand(self):
        """Initialise Command array"""
        try:
            if self.language == "python":
                CMD = ["py", "python3"]
                self.add("cmd", CMD)
            elif self.language == "ruby":
                CMD = ["ruby", "ruby"]
                self.add("cmd", CMD)
            elif self.language in ["c++", "c"]:
                self.makeCParams()
            else:
                err = wp.textWrapBold("Wrong language", "red")
                rprint(f"❌ {err}")
                sys.exit(1)
        except KeyboardInterrupt:
            rprint(
                f"{wp.textWrapBold('Error: ', 'red')}{wp.textWrapBold('KeyboardInterrupt')}"
            )
            sys.exit(1)

    def makePaths(self):
        BASE_DIR = os.getcwd()
        FILE = ""
        THE_FILE = ""
        FILE_TO_WATCH = ""
        THE_FILE_TO_WATCH = ""
        self.add("base_dir", BASE_DIR)
        try:
            if self.get("mode") != "mk":
                if self.get("lang") == "python":
                    # print(python_files)
                    FILE = menu("Choose the file you want to run:", "file")
                elif self.get("lang") == "ruby":
                    # print(ruby_files)
                    FILE = menu("Choose the file you want to run:", "file")

                elif self.get("lang") == "c":
                    FILE = menu("Choose the file you want to run:", "file")

                elif self.get("lang") == "c++":
                    # print(cpp_files)
                    FILE = menu("Choose the file you want to run:", "file")

                if self.get("mode") == "wro":
                    # print(all_files)
                    FILE_TO_WATCH = menu("Choose the file you want to watch:", "file")
            else:
                p = Parser()
                cmds = p.parse()
                if len(cmds) == 0:
                    rprint(
                        f"{wp.textWrapBold('Error: ', 'red')} \
                        {wp.textWrapBold('No make command found')}"
                    )
                    sys.exit(1)
                choices = [(c, c) for c in cmds]
                MK_TO_RUN = menu("Choose the make command to run:", "select", choices)
                self.add("mk_cmd", MK_TO_RUN)

                FILE_TO_WATCH = menu("Choose the file you want to watch:", "file")

                # sys.exit(0)

        except KeyboardInterrupt:
            rprint(
                f"{wp.textWrapBold('Error: ', 'red')}{wp.textWrapBold('KeyboardInterrupt')}"
            )
            sys.exit(1)
        _base = str(self.get("base_dir"))
        if self.get("mode") != "mk":
            THE_FILE = os.path.join(_base, f"{FILE}")
            self.add("the_file", THE_FILE)
        if self.get("mode") in ["wro", "mk"]:
            THE_FILE_TO_WATCH = os.path.join(_base, f"{FILE_TO_WATCH}")
            self.add("the_file_to_watch", THE_FILE_TO_WATCH)
        if self.get("mode") != "mk":
            rprint(self.get("the_file"))
        # Check if the file's path is valid exist
        if self.get("mode") != "mk":
            if not os.path.exists(THE_FILE):
                err = wp.textWrapBold(f"The file {THE_FILE} doesn't exist", "red")
                rprint(f"❌ {err}")
                sys.exit(1)

        # Check if the file's path to watch is valid exist
        if self.get("mode") in ["wro", "mk"] and not os.path.exists(THE_FILE_TO_WATCH):
            err = wp.textWrapBold(
                f"The file {THE_FILE_TO_WATCH} doesn'tOUTPUT_FILE exist", "red"
            )
            rprint(f"❌ {err}")
            sys.exit(1)

        self.make_command_list()

    def make_command_list(self) -> list[str]:
        COMMAND_LIST: list[str] = []
        if self.get("lang") in ["c++", "c"]:
            _cmd : list[str]= []
            _c = self.get("cmd")
            if isinstance(_c, list): _cmd = _c
            COMMAND_LIST = [*_cmd]
            _flags = self.get("flags")
            if isinstance(_flags, list):
                if _flags[0] != "":
                    COMMAND_LIST += [*_flags]
                COMMAND_LIST.append(str(self.get("the_file")))
                COMMAND_LIST.append(str(self.get("output_attr")))
                COMMAND_LIST.append(str(self.get("output_file")))
                self.add("command_list", COMMAND_LIST)
        elif self.get("mode") == "mk":
            COMMAND_LIST = ["make", str(self.get("mk_cmd"))]
            self.add("command_list", COMMAND_LIST)
        else:
            self.add("command_list", None)
        return COMMAND_LIST

    def make(self):
        self.makeMode()
        if self.get("mode") != "mk":
            self.makeLang()
            self.makeCommand()
            self.makePaths()
        else:
            self.makePaths()

    def __str__(self):
        return str(self.entries)

    def __repr__(self):
        return str(self.entries)


class BeautifulOutput:
    def __init__(self, e: Entries =Entries(True)) -> None:
        self.lang = e.get("lang") if not e.is_empty else None
        self.mode = e.get("mode") if not e.is_empty else None
        self.the_file = str(e.get("the_file"))
        self.the_file_to_watch = str(e.get("the_file_to_watch"))


    def _start(self):
        os.system("cls" if os.name == "nt" else "clear")
        f = Figlet(font="colossal", width=80)
        print(f.renderText("Change"))
        print(f.renderText("Detect"))

    def _out(self, lang: str):
        if v.verbose == True:
            custom_fig = Figlet(font="colossal")
            print(custom_fig.renderText(lang))
            if self.mode != "mk":
                rprint(
                    f"{wp.textWrapBold('[FILE] ')}{wp.format_file_path_link(self.the_file)}"
                )
            else:
                rprint(
                    f"{wp.textWrapBold('[FILE] ')}\
                        {wp.format_file_path_link(self.the_file_to_watch)}"
                )
        else:
            if self.mode != "mk":
                rprint(
                    f"{wp.textWrapBold('[FILE] ')}{wp.format_file_path_link(self.the_file)}"
                )
            else:
                rprint(
                    f"{wp.textWrapBold('[FILE] ')}\
                        {wp.format_file_path_link(self.the_file_to_watch)}"
                )

    def _run(self):
        # clear the terminal
        os.system("cls" if os.name == "nt" else "clear")
        if self.lang in ["ruby", "rb"]:
            self._out("Ruby")
        elif self.lang in ["python", "py", "python3"]:
            self._out("Python")
        elif self.lang in ["c++", "cpp"]:
            self._out("C++")
        elif self.lang == "c":
            self._out("C")
        elif self.mode == "mk":
            self._out("Makefile")

    def __str__(self):
        return f"BeautifulOutput({self.lang}, {self.the_file})"


class _Watcher:
    def __init__(
            self,
            handler_type: WrsHandler | WrmHandler | WroHandler | WatchForHandler,
            dir_to_watch: str = os.getcwd()
        ):
        self.DIRECTORY_TO_WATCH = dir_to_watch
        self.observer = Observer()
        self.handler_type = handler_type

    def run(self):
        event_handler = self.handler_type
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except Exception as e:
            self.observer.stop()
            rprint(f"{wp.textWrapBold('Error: ', 'red')}{wp.textWrap(str(e))}")

    def runFor(self, seconds: float):
        event_handler = self.handler_type
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            time.sleep(seconds + 3)
            self.observer.stop()
        except Exception as e:
            self.observer.stop()
            rprint(f"{wp.textWrapBold('Error: ', 'red')}{wp.textWrap(str(e))}")

        self.observer.join()


def activate() -> None:
    """
    ACTIVATE
    --------
    Detect change in the working directory and execute the program chosen.
    Two modes of execution are available to you:
            * Based on observing a specific file for changes
              and executing another file. (Watch and Run Other) `WRO`
            * Observing a certain file and using the same file
              to conduct the test. (Watch and Run Self) `WRS`
    """

    BeautifulOutput()._start()

    try:
        e = Entries()
        e.make()
        _the_file = str(e.get("the_file"))
        _cmd_list: list[str] = []
        _tmp = e.get("command_list")
        if isinstance(_tmp, list): _cmd_list = _tmp
        _lang = str(e.get("lang"))
        _base_dir = str(e.get("base_dir"))
        _cmd: list[str] = []
        _tmp = e.get("cmd")
        if isinstance(_tmp, list): _cmd = _tmp
        wh: WrsHandler | WrmHandler | WroHandler | WatchForHandler
        if e.get("mode") == "wrs":
            wh = WrsHandler(
                the_file=_the_file,
                command_list=_cmd_list,
                language=_lang,
                base_dir=_base_dir,
                cmd=_cmd,
            )
            BeautifulOutput(e)._run()
            mode = wp.textWrapBold("(WRS)", "green")
        elif e.get("mode") == "wro":
            wh = WroHandler(
                the_file=_the_file,
                the_file_to_watch=str(e.get("the_file_to_watch")),
                command_list=_cmd_list,
                language=_lang,
                base_dir=_base_dir,
                cmd=_cmd,
            )
            BeautifulOutput(e)._run()
            mode = wp.textWrapBold("(WRO)", "green")
        else:
            wh = WrmHandler(
                the_file_to_watch=str(e.get("the_file_to_watch")),
                command_list=_cmd_list
            )
            BeautifulOutput(e)._run()
            mode = wp.textWrapBold("(MAKEFILE)", "green")

        w = _Watcher(wh, str(e.get("base_dir")))
        print(" ")
        rprint(f"Watching in {mode} mode...")
        print(" ")
        w.run()
    except KeyboardInterrupt:
        # pipe the error number to the shell
        rprint(
            f"{wp.textWrapBold('Error: ', 'red')}{wp.textWrap('Keyboard Interrupt')}"
        )
        sys.exit(0)

def make_path(base_dir: str, file: str) -> str | None:
    if file == None:
        return None
    if file.startswith(f".{os.sep}"):
        file = file[2:]
    return os.path.join(base_dir, file)

def cfg_activate() -> None:
    """
    CFG ACTIVATE
    ------------
    SAME AS ACTIVATE BUT IT READS THE CONFIG FILE (.detectchange) => a toml file
    """
    base_dir = os.getcwd()
    config_file = os.path.join(base_dir, ".detectchange")
    if not os.path.exists(config_file):
        rprint(
            f"{wp.textWrapBold('Error: ', 'red')}{wp.textWrap('No config file found')}"
        )
        sys.exit(1)
    with open(".detectchange", "rb") as f:
        config = tomli.load(f)

    mode = config.get("mode", "wrs")
    lang = config.get("lang", "python")
    the_file = make_path(os.getcwd(), config.get("file", "main.py"))
    the_file_to_watch = make_path(os.getcwd(), config.get("file_to_watch", None))
    cmd: list[str] = []
    wh: WrsHandler | WrmHandler | WroHandler | WatchForHandler
    verbose = config.get("verbose", False)
    if lang in ["python", "py", "python3"]:
        cmd = config.get("cmd", ["py", "python3"])
    elif lang in ["ruby", "rb"]:
        cmd = config.get("cmd", ["ruby", "ruby"])
    c = config.get("c", {})
    if lang in ["c", "c++", "cpp"]:
        cmd = c.get("cc", None)
    flags = c.get("cflags", " ").split(" ")
    output_attr = c.get("output_attr", "-o")
    output_file = make_path(os.getcwd(), c.get("output", "a.out"))
    if len(cmd) == 0 and lang in ["c", "c++", "cpp"]:
        rprint(
            f"{wp.textWrapBold('Error: ', 'red')}{wp.textWrap('No C compiler found')}"
        )
        sys.exit(1)

    try:
        e = Entries()
        e.add("mode", mode)
        e.add("lang", lang)
        e.add("the_file", the_file)
        e.add("the_file_to_watch", the_file_to_watch)
        e.add("base_dir", base_dir)
        e.add("cmd", cmd)
        e.add("flags", flags)
        e.add("output_attr", output_attr)
        e.add("output_file", output_file)
        cmd_list = e.make_command_list()
        v._verbose = verbose

        if mode == "wrs":
            wh = WrsHandler(
                the_file=str(the_file),
                command_list=cmd_list,
                language=lang,
                base_dir=base_dir,
                cmd=cmd,
            )
            BeautifulOutput(e)._run()
            mode = wp.textWrapBold("(WRS)", "green")
        else:
            wh = WroHandler(
                the_file=str(the_file),
                the_file_to_watch=str(the_file_to_watch),
                command_list=cmd_list,
                language=lang,
                base_dir=base_dir,
                cmd=cmd,
            )
            BeautifulOutput(e)._run()
            mode = wp.textWrapBold("(WRO)", "green")
        w = _Watcher(wh, base_dir)
        print(" ")
        rprint(f"Watching in {mode} mode...")
        print(" ")
        w.run()
    except KeyboardInterrupt:
        # pipe the error number to the shell
        rprint(
            f"{wp.textWrapBold('Error: ', 'red')}{wp.textWrap('Keyboard Interrupt')}"
        )
        sys.exit(0)


def watchFor(ms: int):
    """
    WATCH FOR
    ---------
    Watch for changes in the currentdir and return a json
    """
    res = _Watcher(WatchForHandler(ms)).runFor(ms / 1000)
    rprint(res)


class Assets:
    base_dir = os.path.dirname(os.path.abspath(__file__))

    @classmethod
    def get_version(cls):
        v = VersionControl()
        return f"changedetector\n{v.getVersion()}"

    @classmethod
    def check_version(cls):
        v = VersionControl()
        v.main()


app = typer.Typer(add_completion=True, name="detectchange")


@app.command(help="Get the version of the program")
def version():
    rprint(f"{Assets.get_version()}")
    sys.exit(0)


@app.command(help="Check if there is a new version of the program")
def check():
    Assets.check_version()


@app.command(
    help="Watch for changes in the current directory and execute the program chosen",
    name="watch",
)
def run(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Activate verbose. In this case, the program notify any change"
    ),
    config: bool = typer.Option(
        False,
        "--config",
        "-c",
        help="Use the `.detectchange` config file when you launch the program with this flag"
    ),
):
    if verbose:
        v._verbose = True
    else:
        v._verbose = False
    if config:
        cfg_activate()
    else:
        activate()


if __name__ == "__main__":
    app()
