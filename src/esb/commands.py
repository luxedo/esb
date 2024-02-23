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
import uuid
from datetime import datetime
from functools import wraps
from itertools import product
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from rich.console import Console

from esb.boiler import CodeFurnace
from esb.dash import CliDash
from esb.db import ElvenCrisisArchive
from esb.fetch import RudolphFetcher
from esb.langs import LangMap, LangRunner
from esb.paths import BlankSled, CacheSled, LangSled, find_esb_root, pad_day
from esb.protocol import fireplacev1_0 as fp1_0

if TYPE_CHECKING:
    from esb.langs import LangSpec


COLOR_INFO = "bold green"
COLOR_ERROR = "bold red"
COLOR_WARN = "bold yellow"
console_err = Console(stderr=True)
console_out = Console()

AocParts = Literal[1, 2]


###########################################################
# Decorators
###########################################################
def is_esb_repo(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        repo_root = find_esb_root(Path.cwd())
        if repo_root is None:
            console_err.print(
                "Fatal: this is not an ElfScript Brigade repo.",
                style=COLOR_ERROR,
            )
            sys.exit(2)
        return fn(repo_root, *args, **kwargs)

    return wrapper


###########################################################
# Commands
###########################################################
def new():
    console_err.print("Initializing a new ElfScript Brigade repository", style=COLOR_INFO)
    cwd = Path.cwd()

    bs = BlankSled(Path.cwd())

    if len(bs.repo_conflicts()) > 0:
        console_err.print(
            "Directory not clean! Cannot initialize. Please start the repo in a (somewhat) clean directory.",
            style=COLOR_ERROR,
        )
        sys.exit(1)

    try:
        bs.new_repo()
    except OSError:
        console_err.print("Something went wrong! Could not copy", style=COLOR_ERROR)
        sys.exit(1)

    db = ElvenCrisisArchive(cwd)
    db.create_tables()
    db.ECABrigadista(brigadista_id=str(uuid.uuid4()), creation_date=datetime.now().astimezone()).insert()

    console_err.print(
        "ESB repo is ready! Thank you for saving Christmas [italic]Elf[/italic]",
        style=COLOR_INFO,
    )


@is_esb_repo
def fetch(repo_root: Path, years: list[int], days: list[int], *, force: bool = False):
    db = ElvenCrisisArchive(repo_root)
    for year, day in product(years, days):
        fetch_day(repo_root, db, year, day, force=force)


@is_esb_repo
def start(repo_root: Path, lang: LangSpec, years: list[int], days: list[int], *, force: bool = False):
    db = ElvenCrisisArchive(repo_root)
    for year, day in product(years, days):
        start_day(repo_root, db, lang, year, day, force=force)


@is_esb_repo
def show(repo_root: Path, years: list[int], days: list[int]):
    db = ElvenCrisisArchive(repo_root)
    for year, day in product(years, days):
        show_day(repo_root, db, year, day)


@is_esb_repo
def status(repo_root: Path):
    db = ElvenCrisisArchive(repo_root)
    lmap = LangMap.load()
    cli_dash = CliDash(db, lmap)

    brigadista = cli_dash.brigadista()

    console_out.print("ELFSCRIPT BRIGADE STATUS REPORT\n", style=COLOR_ERROR)
    console_out.print(brigadista, style=COLOR_INFO)
    console_out.print("\nSERVICE STARS", style=COLOR_WARN)

    ys = cli_dash.years_summary()

    for year in sorted(ys.keys(), reverse=True):
        summary = ys[year]
        console_out.print(f"\n{year}")
        console_out.print(f"\n{summary}", style=COLOR_WARN)


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


###########################################################
# Commands per Day
###########################################################
def fetch_day(repo_root: Path, db: ElvenCrisisArchive, year: int, day: int, *, force: bool = False):
    ds = db.ECASolution.find_single({"year": year, "day": day})
    if not force and ds is not None and ds.pt2_answer is not None:
        console_err.print(
            f"Fetch for year {year} day {pad_day(day)} is already complete!",
            style=COLOR_INFO,
        )
        return

    rudolph = RudolphFetcher(repo_root)

    url, statement, pt1_answer, pt2_answer = rudolph.fetch_statement(year, day)

    cache_sled = CacheSled(repo_root)
    st_file = cache_sled.path("statement", year, day)
    st_file.parent.mkdir(parents=True, exist_ok=True)
    st_file.write_text(statement)

    db.ECASolution(year=year, day=day, pt1_answer=pt1_answer, pt2_answer=pt2_answer).insert(replace=True)
    [_, title, *_] = statement.split("---")
    db.ECAProblem(year=year, day=day, title=title.strip(), url=url).insert(replace=True)

    input_file = cache_sled.path("input", year, day)
    if not force and input_file.is_file():
        console_err.print(
            f"Input for year {year} day {pad_day(day)} already cached",
            style=COLOR_INFO,
        )
        return
    puzzle_input = rudolph.fetch_input(year, day)

    input_file.parent.mkdir(parents=True, exist_ok=True)
    input_file.write_text(puzzle_input)
    console_err.print(
        f"Fetched year {year} day {pad_day(day)}!",
        style=COLOR_INFO,
    )


def start_day(repo_root: Path, db: ElvenCrisisArchive, lang: LangSpec, year: int, day: int, *, force: bool):
    day_problem = db.ECAProblem.find_single({"year": year, "day": day})
    match (day_problem, force):
        case (_, True) | (None, _):
            fetch_day(repo_root, db, year, day, force=force)
            day_problem = db.ECAProblem.find_single({"year": year, "day": day})

    day_language = db.ECALanguage.find_single({"year": year, "day": day, "language": lang.name})
    match day_language:
        case db.ECALanguage(started=True):
            console_err.print(
                f'Code for "{lang.name}" year {year} day {pad_day(day)} has already started. '
                "If you wish to overwrite run the command with --force flag.",
                style=COLOR_ERROR,
            )
            return
        # @TODO: Handle started=False

    lang_sled = LangSled.from_spec(repo_root, lang)
    cf = CodeFurnace(lang, lang_sled)
    cf.start(year, day, day_problem.title, day_problem.url)

    db.ECALanguage(
        year=year,
        day=day,
        language=lang.name,
        started=True,
        finished_pt1=False,
        finished_pt2=False,
    ).insert()
    console_err.print(
        f"Started code for {lang.name}, year {year} day {pad_day(day)}",
        style=COLOR_INFO,
    )
    console_err.print(
        f"Open files at {lang_sled.day_dir(year, day)} and happy coding!",
        style=COLOR_INFO,
    )


def show_day(repo_root: Path, db: ElvenCrisisArchive, year: int, day: int):
    ds = db.ECASolution.find_single({"year": year, "day": day})
    cache_sled = CacheSled(repo_root)
    statement_file = cache_sled.path("statement", year, day)
    if ds is None:
        console_err.print(
            f"Solution for year {year} day {pad_day(day)} not cached. Please fetch first",
            style=COLOR_ERROR,
        )
        return

    if not statement_file.is_file():
        console_err.print("Problem not fetched yet!", style=COLOR_ERROR)
    else:
        console_out.print(statement_file.read_text())

    not_solved = "<'Not solved yet'>"
    console_out.print()
    if ds.pt1_answer is not None:
        console_out.print(f"Solution pt1: {ds.pt1_answer}", style=COLOR_INFO)
    else:
        console_out.print(f"Solution pt1: {not_solved}", style=COLOR_ERROR)
    if ds.pt2_answer is not None:
        console_out.print(f"Solution pt2: {ds.pt2_answer}", style=COLOR_INFO)
    else:
        console_out.print(f"Solution pt2: {not_solved}", style=COLOR_ERROR)

    dl = db.ECALanguage.find({"year": year, "day": day})
    if dl is not None:
        console_out.print()
        console_out.print("Languages:", style=COLOR_INFO)
    for eca_language in dl:
        stars = int(eca_language.finished_pt1) + int(eca_language.finished_pt2)
        console_out.print(f"{eca_language.language}: [yellow]{'*' * stars}[/yellow]", style=COLOR_INFO)


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
    dl = db.ECALanguage.find_single({"year": year, "day": day, "language": lang.name})
    if dl is None:
        console_err.print(
            f"Could not find code for year {year} day {pad_day(day)}. Please start first with:",
            style=COLOR_ERROR,
        )
        console_err.print(
            f"esb start --year {year} --day {day} --lang {lang.name}",
        )
        return

    ds = db.ECASolution.find_single({"year": year, "day": day})
    if ds is None:
        console_err.print(
            f"Could not find input for year {year} day {pad_day(day)}. Please fetch first.",
            style=COLOR_ERROR,
        )
        console_err.print(
            f"esb fetch --year {year} --day {day}",
        )
        return

    cache_sled = CacheSled(repo_root)
    lang_sled = LangSled.from_spec(repo_root, lang)
    runner = LangRunner(lang, lang_sled)
    command = runner.build_command(year=year, day=day)
    day_wd = runner.working_dir(year=year, day=day)
    day_input = cache_sled.path("input", year, day)
    result = fp1_0.exec_protocol(command, part, day_wd, day_input)
    match result.status:
        case fp1_0.FPStatus.Ok:
            pass
        case fp1_0.FPStatus.InputDoesNotExists:
            console_err.print(
                (
                    f"\nCould not find input for year {year} day {pad_day(day)}. "
                    "Data seems corrupted. Please fetch again with --force"
                ),
                style=COLOR_ERROR,
            )
            return
        case fp1_0.FPStatus.ProtocolError:
            console_err.print(
                f"\nSolution for year {year} day {pad_day(day)} does not follow FIREPLACE protocol.",
                style=COLOR_ERROR,
            )
            return

    attempt = result.answer
    answer = ds.get_answer(part)
    if answer is not None:
        if attempt == answer:
            console_out.print(f"✔ Answer pt{part}: {attempt}", style=COLOR_INFO)
            dl.set_solved(part)
        else:
            console_out.print(
                f"✘ Answer pt{part}: {attempt}. Expected: {answer}",
                style=COLOR_ERROR,
            )
            dl.set_unsolved(part)
    elif submit:
        # @TODO: implement submit
        ...
    else:
        console_out.print(f"Answer pt{part}: {attempt}", style=COLOR_WARN)
