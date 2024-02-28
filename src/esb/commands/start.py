"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from __future__ import annotations

from itertools import product
from typing import TYPE_CHECKING

from esb.boiler import CodeFurnace
from esb.commands.base import eprint_error, eprint_info, is_esb_repo
from esb.commands.fetch import fetch_day
from esb.db import ElvenCrisisArchive
from esb.paths import LangSled, pad_day

if TYPE_CHECKING:
    from pathlib import Path

    from esb.langs import LangSpec


@is_esb_repo
def start(repo_root: Path, lang: LangSpec, years: list[int], days: list[int], *, force: bool = False):
    db = ElvenCrisisArchive(repo_root)
    for year, day in product(years, days):
        start_day(repo_root, db, lang, year, day, force=force)


def start_day(repo_root: Path, db: ElvenCrisisArchive, lang: LangSpec, year: int, day: int, *, force: bool):
    day_problem = db.ECAPuzzle.find_single({"year": year, "day": day})
    match (day_problem, force):
        case (_, True) | (None, _):
            fetch_day(repo_root, db, year, day, force=force)
            day_problem = db.ECAPuzzle.find_single({"year": year, "day": day})

    day_language = db.ECALanguage.find_single({"year": year, "day": day, "language": lang.name})
    match day_language:
        case db.ECALanguage(started=True):
            eprint_error(
                f'Code for "{lang.name}" year {year} day {pad_day(day)} has already started. '
                "If you wish to overwrite run the command with --force flag.",
            )
            return
        # @TODO: Handle started=False

    lang_sled = LangSled.from_spec(repo_root, lang)
    cf = CodeFurnace(lang, lang_sled)
    cf.start(year, day, day_problem.title, day_problem.url)

    db.ECALanguage(
        year=year,
        day=day,
        language=lang.name,
        started=True,
        finished_pt1=False,
        finished_pt2=False,
    ).insert()
    eprint_info(f"Started code for {lang.name}, year {year} day {pad_day(day)}")
    eprint_info(f"Open files at {lang_sled.day_dir(year, day)} and happy coding!")
