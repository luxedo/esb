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

from esb.commands.base import (
    Command,
    eprint_error,
    eprint_info,
)
from esb.lib.langs import LangRunner, LangSpec
from esb.lib.paths import LangSled, pad_day
from esb.protocol import fireplace


class Test(Command):
    esb_repo: bool = True

    lang: LangSpec
    years: list[int]
    days: list[int]
    parts: list[fireplace.FPPart]
    filter_test: str | None

    def __init__(
        self,
        lang: LangSpec,
        years: list[int],
        days: list[int],
        parts: list[fireplace.FPPart],
        filter_test: str | None = None,
    ):
        super().__init__()
        self.lang = lang
        self.years = years
        self.days = days
        self.parts = parts
        self.filter_test = filter_test
        self.load_from_arg_cache()

    def execute(self):
        for year, day, part in product(self.years, self.days, self.parts):
            self.test_day(self.lang, year, day, part)

    def test_day(
        self,
        lang: LangSpec,
        year: int,
        day: int,
        part: fireplace.FPPart,
    ):
        if self.find_solution(lang, year, day) is None:
            return

        if (tests := self.find_tests(year, day, part, self.filter_test)) == []:
            return

        lang_sled = LangSled.from_spec(self.repo_root, lang)
        runner = LangRunner(lang, lang_sled)

        day_wd = lang_sled.working_dir(year=year, day=day)
        if lang.build_command is not None:
            runner.exec_command(lang.build_command, year, day)

        run_command = runner.prepare_run_command(year=year, day=day)
        for name, test in tests:
            day_input_text = test["input"]
            if "args" in test:
                test["args"] = [str(arg) for arg in test["args"]]
            args = test.get("args")
            eprint_info(f"Testing: {name}. Lang: {lang.name}, year {year} day {pad_day(day)} part {part}")
            result = fireplace.exec_protocol(run_command, part, args, day_wd, day_input_text)
            match (result.status, result.answer == str(test["answer"])):
                case (fireplace.FPStatus.Ok, True):
                    eprint_info(f"✔ Answer pt{part}: {result.answer}")
                case (fireplace.FPStatus.Ok, False):
                    eprint_error(f"✘ Answer pt{part}: {result.answer}. Expected: {test['answer']}")
                case _:
                    eprint_error(f"✘ Could not run {name}")
