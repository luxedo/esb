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
from esb.lib.fetch import RudolphFetcher
from esb.lib.paths import pad_day


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
        if not force and dp is not None and dp.answer_pt2 is not None:
            eprint_error(f"Fetch for year {year} day {pad_day(day)} is already complete!")
            return

        try:
            RudolphFetcher.load_cookie(self.repo_root)
        except ValueError:
            eprint_error(f"Could not load {RudolphFetcher.sess_env} environment variable.")
            sys.exit(2)

        rudolph = RudolphFetcher(self.repo_root)

        url, statement, answer_pt1, answer_pt2 = rudolph.fetch_statement(year, day)

        st_file = self.cache_sled.path("statement", year, day)
        st_file.parent.mkdir(parents=True, exist_ok=True)
        st_file.write_text(statement)

        [_, title, *_] = statement.split("---")

        input_file = self.cache_sled.path("input", year, day)

        if not force and input_file.is_file():
            eprint_info(f"Input for year {year} day {pad_day(day)} already cached")
            return

        try:
            puzzle_input = rudolph.fetch_input(year, day)
        except ValueError as err:
            eprint_error(str(err))
            eprint_error("Visit https://github.com/luxedo/esb/blob/main/doc/SESSION_COOKIE.md for more information")
            sys.exit(2)

        input_file.parent.mkdir(parents=True, exist_ok=True)
        input_file.write_text(puzzle_input)

        tests_file = self.test_sled.path("tests", year, day)
        if not force and tests_file.is_file():
            eprint_info(f"Tests for year {year} day {pad_day(day)} already cached")
        else:
            try:
                tests_input = rudolph.fetch_tests(year, day)
            except ValueError:
                eprint_error("Could not fetch tests. Perhaps they're not available yet.")
            else:
                tests_file.parent.mkdir(parents=True, exist_ok=True)
                tests_file.write_text(tests_input)

        eprint_info(f"Fetched year {year} day {pad_day(day)}!")
        self.db.ECAPuzzle(
            year=year,
            day=day,
            title=title.strip(),
            url=url,
            answer_pt1=answer_pt1,
            answer_pt2=answer_pt2,
            solved_pt1=None,
            solved_pt2=None,
        ).insert(replace=True)
