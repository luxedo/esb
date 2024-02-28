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

from esb.commands.base import eprint_error, eprint_info, is_esb_repo
from esb.db import ElvenCrisisArchive
from esb.fetch import RudolphFetcher
from esb.paths import CacheSled, pad_day

if TYPE_CHECKING:
    from pathlib import Path


@is_esb_repo
def fetch(repo_root: Path, years: list[int], days: list[int], *, force: bool = False):
    db = ElvenCrisisArchive(repo_root)
    for year, day in product(years, days):
        fetch_day(repo_root, db, year, day, force=force)


def fetch_day(repo_root: Path, db: ElvenCrisisArchive, year: int, day: int, *, force: bool = False):
    dp = db.ECAPuzzle.find_single({"year": year, "day": day})
    if not force and dp is not None and dp.pt2_answer is not None:
        eprint_error(f"Fetch for year {year} day {pad_day(day)} is already complete!")
        return

    rudolph = RudolphFetcher(repo_root)

    url, statement, pt1_answer, pt2_answer = rudolph.fetch_statement(year, day)

    cache_sled = CacheSled(repo_root)
    st_file = cache_sled.path("statement", year, day)
    st_file.parent.mkdir(parents=True, exist_ok=True)
    st_file.write_text(statement)

    [_, title, *_] = statement.split("---")
    db.ECAPuzzle(year=year, day=day, title=title.strip(), url=url, pt1_answer=pt1_answer, pt2_answer=pt2_answer).insert(
        replace=True
    )

    input_file = cache_sled.path("input", year, day)
    if not force and input_file.is_file():
        eprint_info(f"Input for year {year} day {pad_day(day)} already cached")
        return
    puzzle_input = rudolph.fetch_input(year, day)

    input_file.parent.mkdir(parents=True, exist_ok=True)
    input_file.write_text(puzzle_input)
    eprint_info(f"Fetched year {year} day {pad_day(day)}!")
