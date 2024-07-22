"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from __future__ import annotations

import sys
from itertools import product

from esb.commands.base import Command, eprint_error, eprint_info
from esb.fetch import RudolphFetcher
from esb.paths import CacheInputSled, pad_day


class Fetch(Command):
    esb_repo: bool = True

    years: list[int]
    days: list[int]
    force: bool

    def __init__(self, years: list[int], days: list[int], *, force: bool = False):
        super().__init__()
        self.years = years
        self.days = days
        self.force = force
        self.load_from_arg_cache()

    def execute(self):
        for year, day in product(self.years, self.days):
            self.fetch_day(year, day, force=self.force)

    def fetch_day(self, year: int, day: int, *, force: bool = False):
        dp = self.db.ECAPuzzle.find_single({"year": year, "day": day})
        if not force and dp is not None and dp.pt2_answer is not None:
            eprint_error(f"Fetch for year {year} day {pad_day(day)} is already complete!")
            return

        try:
            RudolphFetcher.load_cookie(self.repo_root)
        except ValueError:
            eprint_error(f"Could not load {RudolphFetcher.sess_env} environment variable.")
            sys.exit(2)

        rudolph = RudolphFetcher(self.repo_root)

        url, statement, pt1_answer, pt2_answer = rudolph.fetch_statement(year, day)

        cache_sled = CacheInputSled(self.repo_root)
        st_file = cache_sled.path("statement", year, day)
        st_file.parent.mkdir(parents=True, exist_ok=True)
        st_file.write_text(statement)

        [_, title, *_] = statement.split("---")
        self.db.ECAPuzzle(
            year=year, day=day, title=title.strip(), url=url, pt1_answer=pt1_answer, pt2_answer=pt2_answer
        ).insert(replace=True)

        input_file = cache_sled.path("input", year, day)
        if not force and input_file.is_file():
            eprint_info(f"Input for year {year} day {pad_day(day)} already cached")
            return
        puzzle_input = rudolph.fetch_input(year, day)

        input_file.parent.mkdir(parents=True, exist_ok=True)
        input_file.write_text(puzzle_input)
        eprint_info(f"Fetched year {year} day {pad_day(day)}!")
