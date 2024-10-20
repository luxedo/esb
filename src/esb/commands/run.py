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
from datetime import datetime
from itertools import product

from esb.commands.base import Command, eprint_error, eprint_info, eprint_warn
from esb.commands.dashboard import Dashboard
from esb.config import ESBConfig
from esb.lib.fetch import RudolphFetcher, RudolphSubmitStatus
from esb.lib.langs import LangRunner, LangSpec
from esb.lib.paths import LangSled, pad_day
from esb.protocol import fireplace


class Run(Command):
    esb_repo: bool = True

    lang: LangSpec
    years: list[int]
    days: list[int]
    parts: list[fireplace.FPPart]
    submit: bool

    def __init__(
        self, lang: LangSpec, years: list[int], days: list[int], parts: list[fireplace.FPPart], *, submit: bool = False
    ):
        super().__init__()
        self.lang = lang
        self.years = years
        self.days = days
        self.parts = parts
        self.submit = submit
        self.load_from_arg_cache()

    def execute(self):
        for year, day, part in product(self.years, self.days, self.parts):
            self.run_day(self.lang, year, day, part, submit=self.submit)

    def run_day(
        self,
        lang: LangSpec,
        year: int,
        day: int,
        part: fireplace.FPPart,
        *,
        submit: bool,
    ):
        if (dl := self.find_solution(lang, year, day)) is None:
            return

        if (dp := self.find_puzzle(year, day)) is None:
            return

        lang_sled = LangSled.from_spec(self.repo_root, lang)
        runner = LangRunner(lang, lang_sled)

        day_wd = lang_sled.working_dir(year=year, day=day)

        if lang.build_command is not None:
            runner = LangRunner(lang, lang_sled)
            p = runner.exec_command(lang.build_command, year, day)
            if p.returncode != 0:
                eprint_error(f"Could not build program for: {lang.name}, year {year} day {pad_day(day)}")
                sys.exit(2)

        run_command = runner.prepare_run_command(year=year, day=day)
        day_input = self.cache_sled.path("input", year, day)
        args = None

        eprint_info(f"Running solution for: {lang.name}, year {year} day {pad_day(day)} part {part}")
        result = fireplace.exec_protocol_from_file(run_command, part, args, day_wd, day_input)
        match result.status:
            case fireplace.FPStatus.Ok:
                pass
            case fireplace.FPStatus.InputDoesNotExists:
                eprint_error(
                    f"\nCould not find input for year {year} day {pad_day(day)}. "
                    "Data seems corrupted. Please fetch again with --force"
                )
                return
            case fireplace.FPStatus.ProtocolError:
                eprint_error()
                eprint_error(f"Solution for year {year} day {pad_day(day)} does not follow FIREPLACE protocol.")
                return
        attempt = result.answer
        if attempt is not None and len(attempt) > ESBConfig.truncate_answer:
            attempt = f"{attempt[: ESBConfig.truncate_answer]}..."
        answer = dp.get_answer(part)

        now = datetime.now().astimezone()
        self.db.ECARun(
            id=None,
            datetime=now,
            year=year,
            day=day,
            language=lang.name,
            part=part,
            answer=attempt,
            time=result.running_time,
            unit=result.unit,
        ).insert()

        if attempt is not None and submit:
            rudolph = RudolphFetcher(self.repo_root)
            match rudolph.fetch_submit(year, day, part, attempt):
                case RudolphSubmitStatus.SUCCESS:
                    eprint_info("Hooray! Found the answer!")
                    eprint_info(f"✔ Answer pt{part}: {attempt}")
                    now = datetime.now().astimezone()
                    dl.set_solved(part, now)
                    dp.set_solved(part, attempt, now)
                    cmd = Dashboard()
                    cmd.execute()
                case RudolphSubmitStatus.FAIL:
                    eprint_info("That's not the correct answer :'(")
                    eprint_error(f"✘ Answer pt{part}: {attempt}")
                case RudolphSubmitStatus.TIMEOUT:
                    eprint_warn("Cannot submit yet. Please wait before trying again")
                    eprint_warn(f"Answer pt{part}: {attempt}")
                case RudolphSubmitStatus.ALREADY_COMPLETE:
                    eprint_info(
                        "Puzzle already solved but solution not fetched yet. "
                        "Please fetch again to compare solutions.",
                    )
                    eprint_warn(f"Answer pt{part}: {attempt}")
                    now = datetime.now().astimezone()
                    dl.set_solved(part, now)
                    dp.set_solved(part, attempt, now)
                case RudolphSubmitStatus.ERROR:
                    eprint_warn("Unexpected error submitting")
                    eprint_warn(f"Answer pt{part}: {attempt}")
        elif answer is not None:
            if attempt == answer:
                eprint_info(f"✔ Answer pt{part}: {attempt}")
                now = datetime.now().astimezone()
                dl.set_solved(part, now)
                dp.set_solved(part, attempt, now)
            else:
                eprint_error(f"✘ Answer pt{part}: {attempt}. Expected: {answer}")
        else:
            eprint_warn(f"Answer pt{part}: {attempt}")

        if result.unit is not None:
            eprint_warn(f"Running time: {result.running_time} {result.unit.name}seconds")
