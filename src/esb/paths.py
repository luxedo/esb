"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from dataclasses import dataclass, field
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parent
BLANK_DIR = "blank"
LANGS_DIR = "langs"
BOILER_DIR = "boilers"
CACHE_DIR = ".cache"
BOILER_TEMPLATE = "template"
BLANK_ROOT = PACKAGE_ROOT.parent / BLANK_DIR
LANGS_ROOT = PACKAGE_ROOT.parent / LANGS_DIR
BOILER_ROOT = PACKAGE_ROOT.parent / BOILER_DIR
SPEC_FILENAME = "spec.json"


SledFiles = dict[str, str]
SledSubdirs = list[str]


def pad_day(day: int):
    return f"{day:02}"


@dataclass
class YearSled:
    """
    Base class for path manipulation. This class allows for the creation of directories and
    filenames.
    """

    root_dir: Path = field(init=False, default=Path.cwd())
    subdirs: SledSubdirs = field(init=False)
    files: SledFiles = field(init=False)

    @property
    def subdir(self) -> Path:
        return self.root_dir.joinpath(*self.subdirs)

    def year_dir(self, year: int) -> Path:
        return self.subdir / f"{year}"

    def day_dir(self, year: int, day: int) -> Path:
        return self.year_dir(year) / pad_day(day)

    def path(self, file: str, year: int, day: int) -> Path:
        if file not in self.files:
            message = f"Could not find path for file '{file}'"
            raise KeyError(message)
        return self.day_dir(year, day) / self.files[file].format(year=year, day=pad_day(day))


@dataclass
class CacheSled(YearSled):
    subdirs: SledSubdirs = field(default_factory=lambda: [CACHE_DIR])
    files: SledFiles = field(
        default_factory=lambda: {
            "statement": "day_{day}_statement.txt",
            "input": "day_{day}_input.txt",
        }
    )


@dataclass
class LangSled(YearSled):
    name: str
    files: SledFiles

    def __post_init__(self):
        self.subdirs = [LANGS_DIR, self.name]

    def boiler_source(self, filename: str) -> Path:
        return BOILER_ROOT / self.name / BOILER_TEMPLATE / filename

    def boiler_map(self, year: int, day: int) -> dict[Path, Path]:
        return {self.boiler_source(file): self.path(file=file, year=year, day=day) for file in self.files}
