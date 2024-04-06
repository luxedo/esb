"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from esb.config import ESBConfig
from esb.paths import pad_day

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from pathlib import Path
    from typing import Any

    from esb.db import ElvenCrisisArchive, Table
    from esb.langs import LangMap

DayStars = dict[int, int]
YearStars = dict[int, DayStars]
LangStars = dict[str, YearStars]


@dataclass
class BaseDash:
    db: ElvenCrisisArchive
    lmap: LangMap
    SOLVED_NONE: int = field(init=False, default=0)
    SOLVED_PT1: int = field(init=False, default=1)
    SOLVED_PT2: int = field(init=False, default=2)

    @staticmethod
    def groupby(rows: Iterable, key: str) -> dict[Any, Any]:
        ret: dict[Any, Any] = {}
        for row in rows:
            ret.setdefault(getattr(row, key), []).append(row)
        return ret

    def count_stars(self, rows: Iterable, cmp: Callable[[Table], int]) -> YearStars:
        return {
            year: {day: cmp(s) for day, [s] in self.groupby(rows, "day").items()}
            for year, rows in self.groupby(rows, "year").items()
        }

    def fetch_year_stars(self) -> YearStars:
        stats = self.db.ECAPuzzle.fetch_all()

        def cmp_year(s):
            if s.day == ESBConfig.last_day and s.pt1_answer is not None:  # Day 25 has only one star
                return self.SOLVED_PT2
            return (
                self.SOLVED_NONE
                if s.pt1_answer is None
                else self.SOLVED_PT1
                if s.pt2_answer is None
                else self.SOLVED_PT2
            )

        return self.count_stars(stats, cmp_year)

    def fetch_lang_stars(self) -> LangStars:
        langs = self.db.ECALanguage.fetch_all()

        def cmp_lang(s):
            return s.finished_pt1 + s.finished_pt2

        return {lang: self.count_stars(rows, cmp_lang) for lang, rows in self.groupby(langs, "language").items()}

    @staticmethod
    def build_year_str(year: int, days: DayStars) -> str:
        solved_all = (
            all(v == ESBConfig.max_parts for v in days.values()) and len(set(days.keys())) == ESBConfig.last_day
        )
        return f"[yellow]* {year}[/yellow]" if solved_all else f"[yellow]  {year}[/yellow]"

    @staticmethod
    def build_stars_str(days: DayStars, symbol: str) -> str:
        return " ".join([f"{symbol * days.get(day, 0):<2}" for day in range(1, 26)])

    def brigadista(self) -> str:
        b = self.db.ECABrigadista.fetch_single()
        return f"* Brigadista ID: {b.brigadista_id}\n* In Duty Since: {b.creation_date}"


@dataclass
class CliDash(BaseDash):
    def years_summary(self) -> dict[int, str]:
        year_stars = self.fetch_year_stars()
        lang_stars = self.fetch_lang_stars()
        langs = sorted(lang_stars.keys())

        ret = {}
        for year, days in year_stars.items():
            year_title = self.build_year_str(year, days)
            langs_str = "\n".join([
                self.build_stars_str(lang_stars[lang].get(year, {}), self.lmap.get(lang).symbol) for lang in langs
            ]).rstrip()
            stars_str = f'[yellow]{self.build_stars_str(days, "*")}[/yellow]'
            days_str = " ".join([f"{pad_day(day)}" for day in range(1, 26)])
            sep_str = f'[yellow]{"=".join(["==" for _ in range(1, 26)])}[/yellow]'
            ret[year] = f"{year_title}\n{langs_str}\n{stars_str}\n{days_str}\n{sep_str}\n"
        return ret

    def build_dash(self) -> str:
        report = ""
        brigadista = self.brigadista()
        report += "[bold red]ELFSCRIPT BRIGADE STATUS REPORT[/bold red]\n\n"
        report += f"{brigadista}\n\n"
        report += "SERVICE STARS\n"

        ys = self.years_summary()
        for year in sorted(ys.keys(), reverse=True):
            report += f"\n{ys[year]}"
        return report


@dataclass
class MdDash(BaseDash):
    repo_root: Path
    readme: Path = field(init=False)
    start_tag: str = "<!-- Do not delete - Report start -->"
    end_tag: str = "<!-- Do not delete - Report end -->"

    def __post_init__(self):
        self.readme = self.repo_root / "README.md"

    def build_dash(self, *, reset: bool) -> str:
        template = self.load_template(reset=reset)

        brigadista = self.brigadista()
        report = "## ELFSCRIPT BRIGADE STATUS REPORT\n\n"
        report += f"{brigadista}\n\n"
        report += "### SERVICE STARS\n"

        start_idx = template.index(self.start_tag)
        end_idx = template.index(self.end_tag)

        ys = self.years_summary()
        for year in sorted(ys.keys(), reverse=True):
            report += f"\n{ys[year]}"
        report += "\n"

        report = template[: start_idx + len(self.start_tag) + 1] + report + template[end_idx:]

        self.save_report(report)
        return report

    def load_template(self, *, reset: bool) -> str:
        template = ESBConfig.blank_dash.read_text() if reset else self.readme.read_text()

        if self.start_tag not in template:
            message = "Could not find start tag in the markdown file"
            raise ValueError(message)

        if self.end_tag not in template:
            message = "Could not find end tag in the markdown file"
            raise ValueError(message)

        return template

    def save_report(self, report: str):
        self.readme.write_text(report)

    def years_summary(self) -> dict[int, str]:
        year_stars = self.fetch_year_stars()
        lang_stars = self.fetch_lang_stars()

        ret = {}
        for year, days in year_stars.items():
            table0 = self.build_stars_table(year, days, lang_stars, range(1, 11))
            table1 = self.build_stars_table(year, days, lang_stars, range(11, 21))
            table2 = self.build_stars_table(year, days, lang_stars, range(21, 26))
            year_title = f"#### {year}"
            ret[year] = f"\n{year_title}\n\n{table0}\n{table1}\n{table2}"
        return ret

    def build_stars_table(
        self,
        year: int,
        days: dict[int, int],
        lang_stars: LangStars,
        subset: Iterable[int],
    ):
        table_base = """<table>
  {langs_rows}
  <tr>{stars_row}</tr>
  <tr>{days_row}</tr>
</table>"""

        star_map = {
            day: "⭐⭐" if stars == self.SOLVED_PT2 else "⭐☆" if stars == self.SOLVED_PT1 else "☆☆"
            for day, stars in days.items()
        }
        star_row = "".join([f"<td>{star_map.get(day, '☆☆')}</td>" for day in subset])
        days_row = "".join(f"<th>{pad_day(day)}</th>" for day in subset)
        langs_rows = "\n".join(self.build_lang_rows(year, lang_stars, subset))
        return table_base.format(langs_rows=langs_rows, stars_row=star_row, days_row=days_row)

    def build_lang_rows(self, year: int, lang_stars: LangStars, subset: Iterable[int]) -> list[str]:
        langs = []
        for lang, years in lang_stars.items():
            if year not in years or sum(years[year].values()) == 0:
                continue
            emoji = self.lmap.get(lang).emoji
            lang_star_map = {day: emoji * stars for day, stars in years[year].items()}
            lang_row = "".join([f"<td>{lang_star_map.get(day, '☆☆')}</td>" for day in subset])
            langs.append(f"<tr>{lang_row}</tr>")
        return langs
