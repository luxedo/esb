"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from esb.langs import LangSpec

PACKAGE_ROOT = Path(__file__).parent
BLANK_DIR = "blank"
LANGS_DIR = "langs"
CACHE_DIR = ".cache"
BLANK_ROOT = PACKAGE_ROOT.parent / BLANK_DIR
LANGS_ROOT = PACKAGE_ROOT.parent / LANGS_DIR
SPEC_FILENAME = "spec.json"


def pad_day(day: int):
    return f"{day:02}"


@dataclass
class CachePaths:
    cwd: Path

    def cache_year(self, year: int) -> Path:
        return self.cwd / CACHE_DIR / f"{year}"

    def statement_path(self, year: int, day: int) -> Path:
        return self.cache_year(year) / f"day_{pad_day(day)}_statement.txt"

    def input_path(self, year: int, day: int) -> Path:
        return self.cache_year(year) / f"day_{pad_day(day)}_input.txt"


@dataclass
class LangPaths:
    cwd: Path

    def lang_source(self, lang: "LangSpec") -> Path:
        return self.cwd / LANGS_DIR / f"{lang.name}"

    def year_source(self, lang: "LangSpec", year: int) -> Path:
        return self.lang_source(lang) / f"{year}"

    def day_source(self, lang: "LangSpec", year: int, day: int) -> Path:
        return self.year_source(lang, year) / pad_day(day)

    # PEP484 - Forward References https://peps.python.org/pep-0484/#forward-references
    def source(self, lang: "LangSpec", year: int, day: int) -> Path:
        return self.day_source(lang, year, day) / lang.source(year, day)
