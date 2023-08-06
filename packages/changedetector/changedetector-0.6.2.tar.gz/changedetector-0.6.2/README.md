<div align="center">

# changedetector

[![PyPI - Version](https://img.shields.io/pypi/v/changedetector.svg?style=for-the-badge&logo=pypi)](https://pypi.org/project/changedetector)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/changedetector.svg?style=for-the-badge&logo=pypi)](https://pypi.org/project/changedetector)

</div>

## Installation

```sh
pip install changedetector
```

Change detector is a tool that can be used to detect changes in your code-base.
It works with a simple command

```sh
detectchange watch --verbose
```

## Upcomming Features

- [x] Make a config file `.detectchange` -> a toml file **(partial)**
- [x] Read Makefile
- [ ] Add support for more languages

### Config file

```toml
mode="wrs"
lang="c"
file="./src/main.c"
verbose=false

[c]
cc="gcc"
cflags="-Wall -Wextra -Werror"
output="./bin/main"
```

| **commands** | **type** | **required** |           **description**          |
|:------------:|:--------:|:------------:|:----------------------------------:|
|     mode     |    `str`   |      yes     | Mode for detectchange - `wrs` or `wro` |
|     lang     |    `str`   |      yes     | File to excecute language          |
|     file     |    `str`   |      yes     | File to watch                      |
|    verbose   |   `bool`   |      no      | verbose                            |

#### C, Cpp Config

For C and Cpp you need to add a `[c]` section to the config file

```toml
[c]
cc="gcc"
cflags="-Wall -Wextra -Werror"
output="./bin/main"
```

| **commands** | **type** | **required** | **description** |
|:------------:|:--------:|:------------:|:---------------:|
|      cc      |    `str`   |      yes     | The compiler    |
|    cflags    |    `str`   |      no      | Compiler flags  |
|    output    |    `str`   |      no      | Output file     |

It detects changes in your working directory. And executes the scripts chosen
when the script is executed.

It can be used to detect changes in python, ruby, Cpp  and C files.

---

License : MIT
