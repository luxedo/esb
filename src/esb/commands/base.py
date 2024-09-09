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
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console
from rich.theme import Theme

from esb.lib.db import ElvenCrisisArchive
from esb.lib.langs import LangMap
from esb.lib.paths import CacheInputSled, CacheTestSled, find_esb_root, pad_day

if TYPE_CHECKING:
    from esb.lib.db import ECALanguage, ECAPuzzle
    from esb.lib.langs import LangSpec
    from esb.protocol.fireplace import FPPart

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


class Command(ABC):
    db: ElvenCrisisArchive
    repo_root: Path
    lang_map: LangMap
    cache_sled: CacheInputSled
    test_sled: CacheTestSled
    esb_repo: bool = False

    def __init__(self):
        if self.esb_repo:
            repo_root = find_esb_root(Path.cwd())
            if repo_root is None:
                eprint_error("Fatal: this is not an ElfScript Brigade repo.")
                sys.exit(2)
            self.repo_root = repo_root
            self.db = ElvenCrisisArchive(self.repo_root)
            self.lang_map = LangMap.load()
            self.cache_sled = CacheInputSled(self.repo_root)
            self.test_sled = CacheTestSled(self.repo_root)

    @abstractmethod
    def execute(self): ...  # pragma: no cover

    def load_from_arg_cache(self):
        ac = self.db.ECAArgCache.fetch_single()
        if hasattr(self, "years") and len(self.years) == 0:
            if ac.year is None:
                eprint_error("Cannot find cached year. Please run the command passing --year")
                sys.exit(2)
            self.years = [ac.year]
        if hasattr(self, "days") and len(self.days) == 0:
            if ac.day is None:
                eprint_error("Cannot find cached day. Please run the command passing --day")
                sys.exit(2)
            self.days = [ac.day]
        if hasattr(self, "parts") and len(self.parts) == 0:
            if ac.part is None:
                eprint_error("Cannot find cached part. Please run the command passing --part")
                sys.exit(2)
            self.parts = [ac.part]
        if hasattr(self, "lang") and self.lang is None:
            if ac.language is None:
                eprint_error("Cannot find cached language. Please run the command passing --language")
                sys.exit(2)
            self.lang = self.lang_map.get(ac.language)

    def update_arg_cache(self):
        ac = self.db.ECAArgCache.fetch_single()
        if hasattr(self, "years"):
            ac.update({"year": self.years[-1]}, where="id")
        if hasattr(self, "days"):
            ac.update({"day": self.days[-1]}, where="id")
        if hasattr(self, "parts"):
            ac.update({"part": self.parts[-1]}, where="id")
        if hasattr(self, "lang"):
            ac.update({"language": self.lang.name}, where="id")

    def find_test_files(self, year: int, day: int) -> list[Path]:
        ts = CacheTestSled(self.repo_root)
        day_dir = ts.day_dir(year, day)
        return [file for file in day_dir.iterdir() if file.suffix == ".toml"] if day_dir.is_dir() else []

    def find_tests(self, year: int, day: int, part: FPPart, filter_test: str | None = None) -> list[tuple[str, dict]]:
        test_files = self.find_test_files(year, day)
        tests = [test for test_file in test_files for test in self.load_tests(test_file, part)]

        if len(tests) == 0:
            ts = CacheTestSled(self.repo_root)
            day_dir = ts.day_dir(year, day)
            eprint_error(f"Could not find tests for year {year} day {pad_day(day)}")
            eprint_error(f"Create tests at: {day_dir!s}")

        if filter_test is not None:
            tests = [test for test in tests if filter_test in test[0]]
            if len(tests) == 0:
                eprint_error(f'Filter "{filter_test}" did not match any tests')

        return tests

    def find_solution(self, lang: LangSpec, year: int, day: int) -> ECALanguage | None:
        dl = self.db.ECALanguage.find_single({"year": year, "day": day, "language": lang.name})

        if dl is not None:
            return dl
        eprint_error(f"Could not find code for year {year} day {pad_day(day)}. Please start first with:")
        eprint_info(f"esb start --year {year} --day {day} --lang {lang.name}")
        return None

    def find_puzzle(self, year: int, day: int) -> ECAPuzzle | None:
        dp = self.db.ECAPuzzle.find_single({"year": year, "day": day})
        if dp is not None:
            return dp
        eprint_error(f"Could not find input for year {year} day {pad_day(day)}. Please fetch first.")
        eprint_info(
            f"esb fetch --year {year} --day {day}",
        )
        return None

    @staticmethod
    def load_tests(filename: Path, part: FPPart) -> list[tuple[str, dict]]:
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
