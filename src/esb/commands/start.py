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
from typing import TYPE_CHECKING

from esb.boiler import CodeFurnace
from esb.commands.base import Command, eprint_error, eprint_info, eprint_warn
from esb.commands.fetch import Fetch
from esb.langs import LangRunner
from esb.paths import LangSled, pad_day

if TYPE_CHECKING:
    from esb.langs import LangSpec


class Start(Command):
    esb_repo: bool = True

    years: list[int]
    days: list[int]
    force: bool

    def __init__(self, lang: LangSpec, years: list[int], days: list[int], *, force: bool = False):
        super().__init__()
        self.lang = lang
        self.years = years
        self.days = days
        self.force = force

    def execute(self):
        for year, day in product(self.years, self.days):
            self.start_day(self.lang, year, day, force=self.force)

    def start_day(self, lang: LangSpec, year: int, day: int, *, force: bool):
        day_problem = self.db.ECAPuzzle.find_single({"year": year, "day": day})
        match (day_problem, force):
            case (_, True) | (None, _):
                cmd = Fetch(years=[year], days=[day], force=force)
                cmd.execute()
                day_problem = self.db.ECAPuzzle.find_single({"year": year, "day": day})

        day_language = self.db.ECALanguage.find_single({"year": year, "day": day, "language": lang.name})
        match (day_language, force):
            case (None, _):
                pass
            case (self.db.ECALanguage(), True):
                eprint_warn(
                    f'Code for "{lang.name}" year {year} day {pad_day(day)} has already started. ' "Overwritting...",
                )
                day_language.delete()
            case (self.db.ECALanguage(started=True), _):
                eprint_error(
                    f'Code for "{lang.name}" year {year} day {pad_day(day)} has already started. '
                    "If you wish to overwrite run the command with --force flag.",
                )
                return
            # @TODO: Handle started=False

        lang_sled = LangSled.from_spec(self.repo_root, lang)
        cf = CodeFurnace(lang, lang_sled)
        cf.start(year, day, day_problem.title, day_problem.url)

        if lang.install is not None:
            runner = LangRunner(lang, lang_sled)
            p = runner.exec_command(lang.install, year, day)
            if p.returncode != 0:
                eprint_error(f"Could not install program for: {lang.name}, year {year} day {pad_day(day)}")
                sys.exit(2)

        self.db.ECALanguage(
            year=year,
            day=day,
            language=lang.name,
            started=True,
            finished_pt1=False,
            finished_pt2=False,
        ).insert()
        eprint_info(f"Started code for {lang.name}, year {year} day {pad_day(day)}")
        eprint_info(f"Open files at {lang_sled.day_dir(year, day)} and happy coding!")
