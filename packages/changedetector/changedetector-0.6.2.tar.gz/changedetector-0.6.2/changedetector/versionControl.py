import requests
from wrapperComponents import WrapperComponents as wp
from rich import print as rprint
from rich.progress import Progress, SpinnerColumn
from __init__ import __version__


class VersionControl:
    """
    check if there is not more recent package of changedetector
    """

    def __init__(self):
        self.chd_v = __version__
        self.chd_v_split = self.chd_v.split(".")
        self.major = int(self.chd_v_split[0])
        self.minor = int(self.chd_v_split[1])
        self.patch = int(self.chd_v_split[2].split("\n")[0])
        self.version = f"{self.major}.{self.minor}.{self.patch}"

    def upgradeMessage(self):
        return (
            wp.textWrap(
                "There is a newer version of changedetector available", "yellow"
            )
            + "\n"
            + wp.textWrap("Current version: ", "dim")
            + wp.textWrap(f"{self.chd_v}")
            + "\n"
            + wp.textWrap("Latest version: ", "dim")
            + wp.textWrap(f"{self.latest_version}")
            + "\n"
            + wp.textWrap("Run ", "dim")
            + wp.textWrap("pip install --upgrade changedetector")
            + wp.textWrap(" to upgrade", "dim")
        )

    def getVersion(self):
        return self.version

    def check(self):
        globalStr = ""
        try:
            self.latest_version: str = requests.get(
                "https://pypi.org/pypi/changedetector/json"
            ).json()["info"]["version"]
            self.latest_version_split = self.latest_version.split(".")
            self.last_major = int(self.latest_version_split[0])
            self.last_minor = int(self.latest_version_split[1])
            self.last_patch = int(self.latest_version_split[2])

            if self.last_major == self.major:
                if self.last_minor == self.minor and self.last_patch == self.patch:
                    globalStr += wp.textWrap("changedetector is up to date", "green")
                elif (
                    self.last_minor == self.minor
                    and self.last_patch > self.patch
                    or self.last_minor != self.minor
                    and self.last_minor > self.minor
                ):
                    globalStr += "\n" + self.upgradeMessage()
            elif self.last_major > self.major:
                globalStr += "\n" + self.upgradeMessage()

        except requests.exceptions.ConnectionError:
            globalStr += wp.textWrap("Could not check for updates", "red")
        except Exception as e:
            globalStr += wp.textWrap("Could not check for updates", "red")
            rprint(e)
        finally:
            return globalStr

    def main(self):
        pr = Progress(
            SpinnerColumn(),
            "[progress.description]{task.description}",
            transient=True,
        )
        rprint("Changedetector")
        rprint("Version: " + self.getVersion())
        with pr as progress:
            task = progress.add_task("Checking for updates...", total=3)
            progress.update(task, advance=1)
            output = self.check()
            progress.update(task, completed=True)
            rprint(output)


if __name__ == "__main__":
    v = VersionControl()
    v.main()
