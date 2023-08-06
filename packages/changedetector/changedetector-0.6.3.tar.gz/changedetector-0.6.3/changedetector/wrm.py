from watchdog.events import FileSystemEventHandler
import subprocess
import time
from rich import print as rprint
from wrapperComponents import WrapperComponents as wp
from gobals_variables import VARS as v


class WrmHandler(FileSystemEventHandler):
    def __init__(
        self,
        the_file_to_watch: str,
        command_list: list[str],
    ) -> None:
        super().__init__()
        self.language = "Makefile"
        self.the_file_to_watch = the_file_to_watch
        self.command_list = command_list

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
                now = time.perf_counter()
                subprocess.call(self.command_list)
                end = time.perf_counter()
                if v.verbose == True:
                    print("---")
                    rprint(wp.textWrapBold(f"{round(end-now, 2)}s", "bright_magenta"))

                print("---")
                print(f"[{self.language}]", "Listening for changes...")

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
