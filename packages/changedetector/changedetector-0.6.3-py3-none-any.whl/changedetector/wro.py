from watchdog.events import FileSystemEventHandler
import subprocess
import time
import os
from rich import print as rprint
from wrapperComponents import WrapperComponents as wp
from gobals_variables import VARS as v


class WroHandler(FileSystemEventHandler):
    def __init__(
        self,
        the_file: str,
        the_file_to_watch: str,
        language: str,
        command_list: list[str],
        base_dir: str,
        cmd: list,
    ) -> None:
        super().__init__()
        self.the_file = the_file
        self.the_file_to_watch = the_file_to_watch
        self.language = language
        self.command_list = command_list
        self.base_dir = base_dir
        self.cmd = cmd

    def on_any_event(self, event):
        if event.is_directory:
            return None

        elif event.event_type == "created":
            if v.verbose == True:
                rprint(
                    f"{wp.textWrapBold('+ A', 'green')} {wp.textWrapBold(' - {}'.format(wp.format_file_path_link(event.src_path)))}"
                )

        elif event.event_type == "modified":
            # Taken any action here when a file is modified.
            if event.src_path == self.the_file_to_watch:
                print()
                print("---")
                if self.language not in ["c++", "cpp", "c"]:
                    now = time.perf_counter()
                    cm = ""
                    cm = self.cmd[0] if os.name == "nt" else self.cmd[1]
                    subprocess.call([cm, f"{self.the_file}"])
                    end = time.perf_counter()
                else:
                    now = time.perf_counter()
                    subprocess.call(self.command_list)
                    rprint(self.command_list)
                    end = time.perf_counter()
                if v.verbose == True:
                    print("---")
                    rprint(wp.textWrapBold(f"{round(end-now, 2)}s", "bright_magenta"))

                print()
                print("---")
                print(f"[{self.language}]", "Listening for changes...")
            elif event.src_path == f"{self.base_dir}/detectchange.py":
                if v.verbose == True:
                    rprint(
                        wp.textWrapBold(
                            "Detectchange.py has been modified. Please restart the program.",
                            "red",
                        )
                    )
            else:
                if v.verbose == True:
                    rprint(
                        f"{wp.textWrapBold('= M', 'green')} {wp.textWrapBold(' - {}'.format(wp.format_file_path_link(event.src_path)))}"
                    )

        elif event.event_type == "deleted":
            # Taken any action here when a file is deleted.
            if v.verbose == True:
                rprint(
                    f"{wp.textWrapBold('- D', 'red')} {wp.textWrapBold(' - {}'.format(wp.format_file_path_link(event.src_path)))}"
                )
