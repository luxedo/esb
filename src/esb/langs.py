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
from dataclasses import dataclass
from typing import TYPE_CHECKING

from esb.paths import LANGS_ROOT, SPEC_FILENAME

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class LangSpec:
    name: str
    template: Path
    extension: str
    command: list[str]

    @classmethod
    def from_json(cls, file: str | Path):
        with open(file, encoding="utf-8") as fp:
            return cls(**json.load(fp))

    def source(self, year: int, day: int):
        return f"aoc_{year}_{day:02}.{self.extension}"


@dataclass
class LangMap:
    langs: dict[str, LangSpec]

    @classmethod
    def load_defaults(cls):
        return cls({lang.name: LangSpec.from_json(lang / SPEC_FILENAME) for lang in LANGS_ROOT.iterdir()})

    @property
    def names(self):
        return list(self.langs.keys())

    def get(self, key):
        return self.langs[key]
