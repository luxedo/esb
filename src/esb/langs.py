"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from esb.paths import BOILER_ROOT, SPEC_FILENAME, LangSled

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class LangSpec:
    name: str
    files: dict[str, str]
    command: list[str]
    sled: LangSled = field(init=False)

    @classmethod
    def from_json(cls, file: str | Path):
        with open(file, encoding="utf-8") as fp:
            return cls(**json.load(fp))

    def __post_init__(self):
        self.sled = LangSled(name=self.name, files=self.files)

    def run_command(self, year: int, day: int) -> list[str]:
        return [self.replace_files(c, year, day) for c in self.command]

    def replace_files(self, c: str, year: int, day: int) -> str:
        for src, dst in self.sled.boiler_map(year, day).items():
            c = c.replace(f"{{{src.name}}}", dst.name)
        return c


@dataclass
class LangMap:
    langs: dict[str, LangSpec]

    @classmethod
    def load_defaults(cls):
        return cls({lang.name: LangSpec.from_json(lang / SPEC_FILENAME) for lang in BOILER_ROOT.iterdir()})

    @property
    def names(self):
        return list(self.langs.keys())

    def get(self, key):
        return self.langs[key]
