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

from rich.syntax import Syntax

from esb.commands.base import Command, eprint_error, oprint_error, oprint_info, oprint_none
from esb.config import ESBConfig
from esb.lib.paths import pad_day


class Show(Command):
    esb_repo: bool = True

    years: list[int]
    days: list[int]
    show_input: bool = False
    show_test: bool = False

    def __init__(self, years: list[int], days: list[int], *, show_input: bool = False, show_test: bool = False):
        super().__init__()
        self.years = years
        self.days = days
        self.show_input = show_input
        self.show_test = show_test
        self.load_from_arg_cache()

    def execute(self):
        for year, day in product(self.years, self.days):
            self.show_day(year, day, show_input=self.show_input, show_test=self.show_test)

    def show_day(self, year: int, day: int, *, show_input: bool, show_test: bool):
        dp = self.db.ECAPuzzle.find_single({"year": year, "day": day})
        statement_file = self.cache_sled.path("statement", year, day)
        if dp is None:
            eprint_error(f"Solution for year {year} day {pad_day(day)} not cached. Please fetch first")
            return

        if not statement_file.is_file():
            eprint_error("Problem not fetched yet!")
        else:
            oprint_none(statement_file.read_text())

        if show_input:
            input_file = self.cache_sled.path("input", year, day)
            if input_file.is_file():
                oprint_none()
                oprint_none(input_file.read_text())

        if show_test:
            for test_file in self.find_test_files(year, day):
                oprint_none()
                oprint_none(Syntax(test_file.read_text(), "toml"))

        oprint_info()
        oprint_info(f"Advent of Code - {year} day {day}")

        not_solved = "<'Not solved yet'>"
        oprint_info()
        if dp.answer_pt1 is not None:
            oprint_info(f"Solution pt1: {dp.answer_pt1}")
        else:
            oprint_error(f"Solution pt1: {not_solved}")

        if day != ESBConfig.last_day:
            if dp.answer_pt2 is not None:
                oprint_info(f"Solution pt2: {dp.answer_pt2}")
            else:
                oprint_error(f"Solution pt2: {not_solved}")

        dl = self.db.ECALanguage.find({"year": year, "day": day})
        if dl is not None:
            oprint_info()
            oprint_info("Languages:")
        for eca_language in dl:
            stars = int(eca_language.solved_pt1 is not None) + int(eca_language.solved_pt2 is not None)
            oprint_info(f"{eca_language.language}: [yellow]{'*' * stars}[/yellow]")
