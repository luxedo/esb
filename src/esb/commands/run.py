"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from __future__ import annotations

from datetime import datetime
from itertools import product
from typing import TYPE_CHECKING

from esb.commands.base import eprint_error, eprint_info, eprint_warn, find_puzzle, find_solution, is_esb_repo
from esb.db import ElvenCrisisArchive
from esb.fetch import RudolphFetcher, RudolphSubmitStatus
from esb.langs import LangRunner, LangSpec
from esb.paths import CacheSled, LangSled, pad_day
from esb.protocol import fireplacev1_0 as fp1_0

if TYPE_CHECKING:
    from pathlib import Path


@is_esb_repo
def run(
    repo_root: Path,
    lang: LangSpec,
    part: fp1_0.FPPart,
    years: list[int],
    days: list[int],
    *,
    submit: bool = False,
):
    db = ElvenCrisisArchive(repo_root)
    for year, day in product(years, days):
        run_day(repo_root, db, lang, part, year, day, submit=submit)


def run_day(
    repo_root: Path,
    db: ElvenCrisisArchive,
    lang: LangSpec,
    part: fp1_0.FPPart,
    year: int,
    day: int,
    *,
    submit: bool,
):
    if (dl := find_solution(db, year, day, lang)) is None:
        return

    if (dp := find_puzzle(db, year, day)) is None:
        return

    cache_sled = CacheSled(repo_root)
    lang_sled = LangSled.from_spec(repo_root, lang)
    runner = LangRunner(lang, lang_sled)
    command = runner.build_command(year=year, day=day)
    day_wd = runner.working_dir(year=year, day=day)
    day_input = cache_sled.path("input", year, day)
    result = fp1_0.exec_protocol_from_file(command, part, day_wd, day_input)
    match result.status:
        case fp1_0.FPStatus.Ok:
            pass
        case fp1_0.FPStatus.InputDoesNotExists:
            eprint_error(
                f"\nCould not find input for year {year} day {pad_day(day)}. "
                "Data seems corrupted. Please fetch again with --force"
            )
            return
        case fp1_0.FPStatus.ProtocolError:
            eprint_error()
            eprint_error(f"Solution for year {year} day {pad_day(day)} does not follow FIREPLACE protocol.")
            return
    attempt = result.answer
    answer = dp.get_answer(part)

    now = datetime.now().astimezone()
    db.ECARun(
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

    if answer is not None:
        if attempt == answer:
            eprint_info(f"✔ Answer pt{part}: {attempt}")
            dl.set_solved(part)
        else:
            eprint_error(f"✘ Answer pt{part}: {attempt}. Expected: {answer}")
            dl.set_unsolved(part)
        return

    if attempt is not None and submit:
        rudolph = RudolphFetcher(repo_root)
        match rudolph.fetch_submit(year, day, part, attempt):
            case RudolphSubmitStatus.SUCCESS:
                eprint_info("Hooray! Found the answer!")
                eprint_info(f"✔ Answer pt{part}: {attempt}")
            case RudolphSubmitStatus.FAIL:
                eprint_info("That's not the correct answer :'(")
                eprint_error(f"✘ Answer pt{part}: {attempt}")
            case RudolphSubmitStatus.TIMEOUT:
                eprint_warn("Cannot submit yet. Please wait before trying again")
                eprint_warn(f"Answer pt{part}: {attempt}")
            case RudolphSubmitStatus.ALREADY_COMPLETE:
                eprint_info(
                    "Puzzle already solved but solution not fetched yet. " "Please fetch again to compare solutions.",
                )
                eprint_warn(f"Answer pt{part}: {attempt}")
            case RudolphSubmitStatus.ERROR:
                eprint_warn("Unexpected error submitting")
                eprint_warn(f"Answer pt{part}: {attempt}")
    else:
        eprint_warn(f"Answer pt{part}: {attempt}")
