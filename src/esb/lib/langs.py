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
import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING

from esb.config import ESBConfig
from esb.lib.paths import pad_day

if TYPE_CHECKING:
    from pathlib import Path

    from esb.lib.paths import LangSled


@dataclass
class LangSpec:
    name: str
    files: dict[str, str]
    run_command: list[str]
    symbol: str
    emoji: str
    base: bool = False
    build_command: list[str] | None = None
    install: list[str] | None = None

    @classmethod
    def from_json(cls, file: str | Path):
        with open(file, encoding="utf-8") as fp:
            return cls(**json.load(fp))


@dataclass
class LangMap:
    langs: dict[str, LangSpec]

    @classmethod
    def load_defaults(cls):
        return cls({
            lang.name: LangSpec.from_json(lang / ESBConfig.spec_filename) for lang in ESBConfig.boiler_root.iterdir()
        })

    @classmethod
    def load(cls):
        return cls.load_defaults()

    @property
    def names(self):
        return list(self.langs.keys())

    def get(self, key):
        return self.langs[key]


@dataclass
class LangRunner:
    spec: LangSpec
    sled: LangSled

    def prepare_install_command(self, year: int, day: int) -> list[str]:
        if self.spec.install is None:
            message = f"Cannot prepare install command because it does not exists for language {self.spec.name}"
            raise TypeError(message)
        return self.prepare_command(self.spec.install, year, day)

    def prepare_build_command(self, year: int, day: int) -> list[str]:
        if self.spec.build_command is None:
            message = f"Cannot prepare build command because it does not exists for language {self.spec.name}"
            raise TypeError(message)
        return self.prepare_command(self.spec.build_command, year, day)

    def prepare_run_command(self, year: int, day: int) -> list[str]:
        return self.prepare_command(self.spec.run_command, year, day)

    def prepare_command(self, command: list[str], year: int, day: int) -> list[str]:
        return [self.replace_files(c, year, day) for c in command]

    def replace_files(self, c: str, year: int, day: int) -> str:
        filenames = {k.name: v.name for k, v in self.sled.boiler_map(year, day).items()}
        replace_mapping = {
            "year": year,
            "day": pad_day(day),
            "filenames": filenames,
        }
        return c.format_map(replace_mapping)

    def exec_command(self, command: list[str], year: int, day: int) -> subprocess.CompletedProcess:
        day_wd = self.sled.working_dir(year=year, day=day)
        command = self.prepare_command(command, year=year, day=day)
        return subprocess.run(command, cwd=day_wd, check=False)
