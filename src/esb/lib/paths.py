"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Self

from esb.config import ESBConfig

if TYPE_CHECKING:
    from esb.lib.langs import LangSpec


SledFiles = dict[str, str]
SledSubdirs = list[str]


def pad_day(day: int):
    return f"{day:02}"


def find_esb_root(cwd: Path) -> Path | None:
    if cwd == Path("/"):
        return None
    if (cwd / ESBConfig.db_path).is_file():
        return cwd
    return find_esb_root(cwd.parent)


@dataclass
class BlankSled:
    repo_root: Path

    def repo_conflicts(self):
        return [
            self.repo_root / item.name
            for item in ESBConfig.blank_root.iterdir()
            if (self.repo_root / item.name).is_dir() or (self.repo_root / item.name).is_file()
        ]

    def new_repo(self):
        for item in ESBConfig.blank_root.iterdir():
            if item.is_dir():
                shutil.copytree(item, self.repo_root / item.name)
            else:
                shutil.copy(item, self.repo_root)


@dataclass
class YearSled:
    repo_root: Path
    subdirs: SledSubdirs = field(init=False)
    files: SledFiles = field(init=False)

    @property
    def subdir(self) -> Path:
        if self.repo_root is None:
            message = "Could not find an ESB repo in the current path"
            raise ValueError(message)
        return self.repo_root.joinpath(*self.subdirs)

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
class CacheInputSled(YearSled):
    subdirs: SledSubdirs = field(default_factory=lambda: [ESBConfig.cache_dir])
    files: SledFiles = field(
        default_factory=lambda: {
            "statement": "day_{day}_statement.txt",
            "input": "day_{day}_input.txt",
        }
    )


@dataclass
class CacheTestSled(YearSled):
    subdirs: SledSubdirs = field(default_factory=lambda: [ESBConfig.tests_dir])
    files: SledFiles = field(
        default_factory=lambda: {
            "tests": "tests_{year}_{day}.toml",
        }
    )


@dataclass
class LangSled(YearSled):
    name: str
    files: SledFiles

    @classmethod
    def from_spec(cls, repo_root: Path, spec: LangSpec) -> Self:
        return cls(repo_root=repo_root, name=spec.name, files=spec.files)

    def __post_init__(self):
        self.subdirs = [ESBConfig.solutions_dir, self.name]

    @property
    def boiler_subdir(self) -> Path:
        return ESBConfig.boiler_root / self.name / ESBConfig.boiler_template

    @property
    def boiler_base_subdir(self) -> Path:
        return self.boiler_subdir.parent / ESBConfig.boiler_template_base

    def boiler_source(self, filename: str) -> Path:
        return self.boiler_subdir / filename

    def boiler_map(self, year: int, day: int) -> dict[Path, Path]:
        return {self.boiler_source(file): self.path(file=file, year=year, day=day) for file in self.files}

    def copied_source(self, year: int, day: int, filename: str) -> Path:
        return self.day_dir(year, day) / filename

    def copied_map(self, year: int, day: int) -> dict[Path, Path]:
        return {self.copied_source(year, day, file): self.path(file=file, year=year, day=day) for file in self.files}

    def working_dir(self, year: int, day: int) -> Path:
        return self.day_dir(year, day)
