from enum import Enum
import os

class SpecialTokens(Enum):
    PHONY = ".PHONY"
    SUFFIXES = ".SUFFIXES"
    DEFAULT_GOAL = ".DEFAULT_GOAL"
    PRECIOUS = ".PRECIOUS"
    SECONDARY = ".SECONDARY"
    INTERMEDIATE = ".INTERMEDIATE"
    SILENT = ".SILENT"
    EXPORT_ALL_VARIABLES = ".EXPORT_ALL_VARIABLES"
    NOTPARALLEL = ".NOTPARALLEL"
    ONESHELL = ".ONESHELL"

class Parser():
    def __init__(self) -> None:
        self.sepecials = [x.value for x in SpecialTokens]
        pass

    def parse(self):
        mk_path = os.path.join(os.getcwd(), 'Makefile')
        with open(mk_path, "r") as f:
            temp = f.readlines()
            lines = []
            for line in temp:
                if not line.startswith("#") and not line.startswith("\t") and not line.startswith("$") and not line.startswith("define") and not line.startswith("endef") and not line.startswith("endif") and not line.startswith("else") and not line.startswith("ifndef") and not line.startswith("ifeq") and not ":=" in line and not line.startswith("@") and not line.startswith("-"):
                    if line != "\n":
                        special, command = self.isspecial(line)
                        if not special and command not in lines:
                            lines.append(command)
        return lines

    def isspecial(self, line: str) -> tuple[bool, str]:
        l  = line.split(":")
        return (True, l[0]) if l[0] in self.sepecials else (False, l[0])

if __name__ == "__main__":
    p = Parser()
    print(p.parse())
