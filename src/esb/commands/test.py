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

from esb.commands.base import (
    eprint_error,
    eprint_info,
    find_solution,
    find_tests,
    is_esb_repo,
)
from esb.db import ElvenCrisisArchive
from esb.langs import LangRunner, LangSpec
from esb.paths import LangSled
from esb.protocol import fireplacev1_0 as fp1_0

if TYPE_CHECKING:
    from pathlib import Path


@is_esb_repo
def test(
    repo_root: Path,
    lang: LangSpec,
    part: fp1_0.FPPart,
    years: list[int],
    days: list[int],
):
    db = ElvenCrisisArchive(repo_root)
    for year, day in product(years, days):
        test_day(repo_root, db, lang, part, year, day)


def test_day(
    repo_root: Path,
    db: ElvenCrisisArchive,
    lang: LangSpec,
    part: fp1_0.FPPart,
    year: int,
    day: int,
):
    if find_solution(db, year, day, lang) is None:
        return

    if (tests := find_tests(repo_root, year, day, part)) == []:
        return

    lang_sled = LangSled.from_spec(repo_root, lang)
    runner = LangRunner(lang, lang_sled)
    command = runner.build_command(year=year, day=day)
    day_wd = runner.working_dir(year=year, day=day)
    for name, test in tests:
        day_input_text = test["input"]
        result = fp1_0.exec_protocol(command, part, day_wd, day_input_text)
        match (result.status, result.answer == test["answer"]):
            case (fp1_0.FPStatus.Ok, True):
                eprint_info(f"✔ Answer {name} pt{part}: {result.answer}")
            case (fp1_0.FPStatus.Ok, False):
                eprint_error(f"✘ Answer {name} pt{part}: {result.answer}. Expected: {test['answer']}")
            case _:
                eprint_error(f"✘ Could not run {name}")
