"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from pathlib import Path


def year_path(year: int) -> Path:
    return Path.cwd() / ".cache" / f"{year}"


def statement_path(year: int, day: int) -> Path:
    return year_path(year) / f"day_{day:02}_statement.txt"


def input_path(year: int, day: int) -> Path:
    return year_path(year) / f"day_{day:02}_input.txt"
