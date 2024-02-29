"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from __future__ import annotations

import sys
import tomllib
from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console
from rich.theme import Theme

from esb.paths import TestSled, find_esb_root, pad_day

if TYPE_CHECKING:
    from esb.db import ECALanguage, ECAPuzzle, ElvenCrisisArchive
    from esb.langs import LangSpec
    from esb.protocol import fireplacev1_0 as fp1_0

COLOR_INFO = "bold green"
COLOR_ERROR = "bold red"
COLOR_WARN = "bold yellow"
eprint_info = Console(stderr=True, style=COLOR_INFO).print
eprint_error = Console(stderr=True, style=COLOR_ERROR).print
eprint_none = Console(stderr=True, theme=Theme(inherit=False)).print
eprint_warn = Console(stderr=True, style=COLOR_WARN).print
oprint_info = Console(style=COLOR_INFO).print
oprint_error = Console(style=COLOR_ERROR).print
oprint_none = Console(theme=Theme(inherit=False)).print
oprint_warn = Console(style=COLOR_WARN).print


def is_esb_repo(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        repo_root = find_esb_root(Path.cwd())
        if repo_root is None:
            eprint_error("Fatal: this is not an ElfScript Brigade repo.")
            sys.exit(2)
        return fn(repo_root, *args, **kwargs)

    return wrapper


def find_solution(db: ElvenCrisisArchive, year: int, day: int, lang: LangSpec) -> ECALanguage | None:
    dl = db.ECALanguage.find_single({"year": year, "day": day, "language": lang.name})

    if dl is not None:
        return dl
    eprint_error(f"Could not find code for year {year} day {pad_day(day)}. Please start first with:")
    eprint_info(f"esb start --year {year} --day {day} --lang {lang.name}")
    return None


def find_puzzle(db: ElvenCrisisArchive, year: int, day: int) -> ECAPuzzle | None:
    dp = db.ECAPuzzle.find_single({"year": year, "day": day})
    if dp is not None:
        return dp
    eprint_error(f"Could not find input for year {year} day {pad_day(day)}. Please fetch first.")
    eprint_info(
        f"esb fetch --year {year} --day {day}",
    )
    return None


def find_tests(repo_root: Path, year: int, day: int, part: fp1_0.FPPart) -> list[tuple[str, dict]]:
    ts = TestSled(repo_root)
    day_dir = ts.day_dir(year, day)

    test_files = [file for file in day_dir.iterdir() if file.suffix == ".toml"] if day_dir.is_dir() else []

    tests = [test for test_file in test_files for test in load_tests(test_file, part)]

    if len(tests) == 0:
        eprint_error(f"Could not find tests for year {year} day {pad_day(day)}")
        eprint_error(f"Create tests at: {day_dir!s}")
    return tests


def load_tests(filename: Path, part: fp1_0.FPPart) -> list[tuple[str, dict]]:
    cases_str = filename.read_text()
    try:
        cases = tomllib.loads(cases_str).get("test", {})
    except tomllib.TOMLDecodeError:
        eprint_error(f"Test file {filename.name} is malformed")
        return []

    tests = []
    for name, c in cases.items():
        test_name = f"{filename.stem}.{name}"
        if not all(key in c for key in ["input", "answer", "part"]):
            eprint_error(f'Test {test_name} is missing one of the following keys: "input", "answer" or "part"')
            continue
        if c["part"] == part:
            tests.append((test_name, c))
    return tests
