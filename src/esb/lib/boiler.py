"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from typing import TYPE_CHECKING

from esb.lib.paths import CacheTestSled, pad_day

if TYPE_CHECKING:
    from pathlib import Path

    from esb.lib.langs import LangSpec
    from esb.lib.paths import LangSled


@dataclass
class CodeFurnace:
    lang_spec: LangSpec
    lang_sled: LangSled

    def start(self, year: int, day: int, title: str, url: str):
        dst_dir = self.lang_sled.day_dir(year, day)
        if dst_dir.is_dir():
            shutil.rmtree(dst_dir)

        if self.lang_spec.base:
            self.copy_base(dst_dir)

        self.copy_template(year, day, title, url)

        self.make_test_dir(year, day)

    def copy_base(self, dst_dir: Path):
        base_dir = self.lang_sled.boiler_base_subdir
        shutil.copytree(base_dir, dst_dir)

    def copy_template(self, year: int, day: int, title: str, url: str):
        src_dir = self.lang_sled.boiler_subdir
        dst_dir = self.lang_sled.day_dir(year, day)
        shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)

        for src, dst in self.lang_sled.copied_map(year, day).items():
            shutil.move(src, dst)
            content = self.safe_format(
                dst.read_text(),
                year=year,
                day=pad_day(day),
                language=self.lang_sled.name,
                problem_title=title,
                problem_url=url,
            )
            dst.write_text(content)

    def make_test_dir(self, year: int, day: int):
        ts = CacheTestSled(self.lang_sled.repo_root)
        day_dir = ts.day_dir(year, day)
        if not day_dir.is_dir():
            day_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def safe_format(template: str, **patterns) -> str:
        result = template
        for key, val in patterns.items():
            m = f"{{{key}}}"
            result = result.replace(m, str(val))
        return result
