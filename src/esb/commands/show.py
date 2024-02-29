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

from esb.commands.base import eprint_error, is_esb_repo, oprint_error, oprint_info, oprint_none
from esb.config import ESBConfig
from esb.db import ElvenCrisisArchive
from esb.paths import CacheSled, pad_day

if TYPE_CHECKING:
    from pathlib import Path


@is_esb_repo
def show(repo_root: Path, years: list[int], days: list[int]):
    db = ElvenCrisisArchive(repo_root)
    for year, day in product(years, days):
        show_day(repo_root, db, year, day)


def show_day(repo_root: Path, db: ElvenCrisisArchive, year: int, day: int):
    dp = db.ECAPuzzle.find_single({"year": year, "day": day})
    cache_sled = CacheSled(repo_root)
    statement_file = cache_sled.path("statement", year, day)
    if dp is None:
        eprint_error(f"Solution for year {year} day {pad_day(day)} not cached. Please fetch first")
        return

    if not statement_file.is_file():
        eprint_error("Problem not fetched yet!")
    else:
        oprint_none(statement_file.read_text())

    not_solved = "<'Not solved yet'>"
    oprint_info()
    if dp.pt1_answer is not None:
        oprint_info(f"Solution pt1: {dp.pt1_answer}")
    else:
        oprint_error(f"Solution pt1: {not_solved}")

    if day != ESBConfig.last_day:
        if dp.pt2_answer is not None:
            oprint_info(f"Solution pt2: {dp.pt2_answer}")
        else:
            oprint_error(f"Solution pt2: {not_solved}")

    dl = db.ECALanguage.find({"year": year, "day": day})
    if dl is not None:
        oprint_info()
        oprint_info("Languages:")
    for eca_language in dl:
        stars = int(eca_language.finished_pt1) + int(eca_language.finished_pt2)
        oprint_info(f"{eca_language.language}: [yellow]{'*' * stars}[/yellow]")
