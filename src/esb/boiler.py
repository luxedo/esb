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

from esb.paths import pad_day

if TYPE_CHECKING:
    from esb.langs import LangSpec
    from esb.paths import LangSled


@dataclass
class CodeFurnace:
    lang_spec: LangSpec
    lang_sled: LangSled

    def start(self, year: int, day: int, title: str, url: str):
        src_dir = self.lang_sled.boiler_subdir
        dst_dir = self.lang_sled.day_dir(year, day)
        if dst_dir.is_dir():
            shutil.rmtree(dst_dir)
        shutil.copytree(src_dir, dst_dir)

        for src, dst in self.lang_sled.copied_map(year, day).items():
            shutil.move(src, dst)
            content = dst.read_text().format(
                year=year,
                day=pad_day(day),
                problem_title=title,
                problem_url=url,
            )
            dst.write_text(content)
