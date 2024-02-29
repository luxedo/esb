"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from esb.config import ESBConfig
from esb.paths import pad_day

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from typing import Any

    from esb.db import ElvenCrisisArchive, Table
    from esb.langs import LangMap


@dataclass
class CliDash:
    db: ElvenCrisisArchive
    lmap: LangMap

    @staticmethod
    def groupby(rows: Iterable, key: str) -> dict[Any, Any]:
        ret: dict[Any, Any] = {}
        for row in rows:
            ret.setdefault(getattr(row, key), []).append(row)
        return ret

    def count_stars(self, rows: Iterable, cmp: Callable[[Table], int]) -> dict[int, dict[int, int]]:
        return {
            year: {day: cmp(s) for day, [s] in self.groupby(rows, "day").items()}
            for year, rows in self.groupby(rows, "year").items()
        }

    def fetch_year_stars(self) -> dict[int, dict[int, int]]:
        stats = self.db.ECAPuzzle.fetch_all()

        def cmp_year(s):
            if s.day == ESBConfig.last_day and s.pt1_answer is not None:  # Day 25 has only one star
                return 2
            return 0 if s.pt1_answer is None else 1 if s.pt2_answer is None else 2

        return self.count_stars(stats, cmp_year)

    def fetch_lang_stars(self) -> dict[str, dict[int, dict[int, int]]]:
        langs = self.db.ECALanguage.fetch_all()

        def cmp_lang(s):
            return s.finished_pt1 + s.finished_pt2

        return {lang: self.count_stars(rows, cmp_lang) for lang, rows in self.groupby(langs, "language").items()}

    @staticmethod
    def build_stars_str(days: dict[int, int], symbol: str) -> str:
        return " ".join([f"{symbol * days.get(day, 0):<2}" for day in range(1, 26)])

    def brigadista(self) -> str:
        b = self.db.ECABrigadista.fetch_single()
        return f"Brigadista ID: {b.brigadista_id}\nIn Duty Since: {b.creation_date}"

    def years_summary(self) -> dict[int, str]:
        year_stars = self.fetch_year_stars()
        lang_stars = self.fetch_lang_stars()
        langs = sorted(lang_stars.keys())

        ret = {}
        for year, days in year_stars.items():
            langs_str = "\n".join([
                self.build_stars_str(lang_stars[lang].get(year, {}), self.lmap.get(lang).symbol) for lang in langs
            ])
            stars_str = self.build_stars_str(days, "*")
            days_str = " ".join([f"{pad_day(day)}" for day in range(1, 26)])
            sep_str = "=".join(["==" for day in range(1, 26)])
            summary = f"{langs_str}\n{stars_str}\n{days_str}\n{sep_str}"
            ret[year] = summary
        return ret
