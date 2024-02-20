"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from __future__ import annotations

import http.client
import re
import shutil
import sys
import uuid
from datetime import datetime
from itertools import product
from os import environ
from pathlib import Path
from textwrap import wrap
from typing import TYPE_CHECKING, Literal

from bs4 import BeautifulSoup
from rich.console import Console

from esb import __version__
from esb.boiler import CodeFurnace
from esb.db import ElvenCrisisArchive
from esb.paths import BLANK_ROOT, CacheSled, pad_day
from esb.protocol import fireplacev1_0 as fp1_0

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any

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
    def wrapper(*args, **kwargs):
        if not ElvenCrisisArchive.has_db():
            console_err.print(
                "Fatal: this is not an ElfScript Brigade repo.",
                style=COLOR_ERROR,
            )
            sys.exit(2)
        return fn(*args, **kwargs)

    # @TODO
    return wrapper


###########################################################
# Commands
###########################################################
def new():
    console_err.print("Initializing a new ElfScript Brigade repository", style=COLOR_INFO)
    cwd = Path.cwd()

    if len(_repo_conflicts(cwd)) > 0:
        console_err.print(
            "Directory not clean! Cannot initialize. Please start the repo in a (somewhat) clean directory.",
            style=COLOR_ERROR,
        )
        sys.exit(1)

    try:
        _copy_blank_repo(cwd)
    except OSError:
        console_err.print("Something went wrong! Could not copy", style=COLOR_ERROR)
        sys.exit(1)

    db = ElvenCrisisArchive()

    db.create_tables()

    db.ECABrigadista(brigadista_id=str(uuid.uuid4()), creation_date=datetime.now().astimezone()).insert()

    console_err.print(
        "ESB repo is ready! Thank you for saving Christmas [italic]Elf[/italic]",
        style=COLOR_INFO,
    )


@is_esb_repo
def fetch(years: list[int], days: list[int], *, force: bool = False):
    db = ElvenCrisisArchive()
    for year, day in product(years, days):
        fetch_day(db, year, day, force=force)


@is_esb_repo
def start(lang: LangSpec, years: list[int], days: list[int], *, force: bool = False):
    db = ElvenCrisisArchive()
    for year, day in product(years, days):
        start_day(db, lang, year, day, force=force)


@is_esb_repo
def show(years: list[int], days: list[int]):
    db = ElvenCrisisArchive()
    for year, day in product(years, days):
        show_day(db, year, day)


###########################################################
# Commands per Day
###########################################################
def fetch_day(db: ElvenCrisisArchive, year: int, day: int, *, force: bool = False):
    ds = db.ECASolution.find_single({"year": year, "day": day})
    if not force and ds is not None and ds.pt2_answer is not None:
        console_err.print(
            f"Fetch for year {year} day {pad_day(day)} is already complete!",
            style=COLOR_INFO,
        )
        return

    host = "adventofcode.com"
    cookie = _load_cookie()
    cache_sled = CacheSled()

    st_route = f"/{year}/day/{day}"
    st_html = _fetch_url(host, st_route, cookie)
    statement, pt1_answer, pt2_answer = _parse_body(st_html)
    st_file = cache_sled.path("statement", year, day)
    st_file.parent.mkdir(parents=True, exist_ok=True)
    st_file.write_text(statement)

    db.ECASolution(year=year, day=day, pt1_answer=pt1_answer, pt2_answer=pt2_answer).insert(replace=True)
    [_, title, *_] = statement.split("---")
    db.ECAProblem(year=year, day=day, title=title.strip(), url=host + st_route).insert(replace=True)

    input_file = cache_sled.path("input", year, day)
    if not force and input_file.is_file():
        console_err.print(
            f"Input for year {year} day {pad_day(day)} already cached",
            style=COLOR_INFO,
        )
        return
    input_route = f"{st_route}/input"
    puzzle_input = _fetch_url(host, input_route, cookie)
    input_file.parent.mkdir(parents=True, exist_ok=True)
    input_file.write_text(puzzle_input)
    console_err.print(
        f"Fetched year {year} day {pad_day(day)}!",
        style=COLOR_INFO,
    )


def start_day(db: ElvenCrisisArchive, lang: LangSpec, year: int, day: int, *, force: bool):
    day_problem = db.ECAProblem.find_single({"year": year, "day": day})
    match (day_problem, force):
        case (_, True) | (None, _):
            fetch_day(db, year, day, force=force)
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

    cf = CodeFurnace(lang)
    cf.start(year, day, day_problem.title, day_problem.url)

    db.ECALanguage(
        year=year,
        day=day,
        language=lang.name,
        started=True,
        finished_pt1=False,
        finished_pt2=False,
    ).insert()


def show_day(db: ElvenCrisisArchive, year: int, day: int):
    ds = db.ECASolution.find_single({"year": year, "day": day})
    cache_sled = CacheSled()
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


@is_esb_repo
def status():
    db = ElvenCrisisArchive()
    info = db.ECABrigadista.fetch_single()
    console_out.print(
        "ELFSCRIPT BRIGADE STATUS REPORT\n",
        style=COLOR_ERROR,
    )
    console_out.print(
        f"Brigadista ID: {info.brigadista_id}\nIn Duty Since: {info.creation_date}\n",
        style=COLOR_INFO,
    )
    console_out.print(
        "SERVICE STARS",
        style=COLOR_WARN,
    )

    cwd = Path.cwd()
    ys = _years_summary(db, cwd)
    for year in sorted(ys.keys(), reverse=True):
        summary = ys[year]
        console_out.print(
            f"\n{summary}\n{year}",
            style=COLOR_WARN,
        )


@is_esb_repo
def run(
    lang: LangSpec,
    part: fp1_0.FPPart,
    years: list[int],
    days: list[int],
    *,
    submit: bool = False,
):
    db = ElvenCrisisArchive()
    for year, day in product(years, days):
        run_day(db, lang, part, year, day, submit=submit)


def run_day(
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

    cache_sled = CacheSled()
    command = lang.build_command(year=year, day=day)
    day_wd = lang.sled.day_dir(year=year, day=day)
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


###########################################################
# Helper functions
###########################################################
def _repo_conflicts(cwd):
    return [
        cwd / item.name for item in BLANK_ROOT.iterdir() if (cwd / item.name).is_dir() or (cwd / item.name).is_file()
    ]


def _copy_blank_repo(cwd):
    for item in BLANK_ROOT.iterdir():
        if item.is_dir():
            shutil.copytree(item, cwd / item.name)
        else:
            shutil.copy(item, cwd)


def _load_cookie() -> str:
    cwd = Path.cwd()
    sess_env = "AOC_SESSION_COOKIE"
    dotenv = cwd / ".env"
    if dotenv.is_file():
        with dotenv.open() as fp:
            match [line.split("=")[1] for line in fp.read().split("\n") if line.startswith(sess_env)]:
                case [dot_cookie]:
                    return dot_cookie.removeprefix('"').removesuffix('"')
    env_cookie: str | None = environ.get(sess_env)
    match env_cookie:
        case None:
            message = f"Could not find {sess_env}"
            raise ValueError(message)
        case str(_):
            return env_cookie


def _fetch_url(host: str, route: str, cookie: str) -> str:
    conn = http.client.HTTPSConnection(host)
    conn.request(
        "GET",
        route,
        headers={
            "Cookie": f"session={cookie}",
            "User-Agent": f"ElfScipt Brigade/{__version__}; github.com/luxedo/esb by luizamaral306@gmail.com",
        },
    )
    res = conn.getresponse()
    http_ok = 200
    if res.status != http_ok:
        message = "Could not fetch! Maybe your cookie have expired"
        raise ValueError(message)
    return res.read().decode("utf-8")


def _parse_body(body: str) -> tuple[str, str | None, str | None]:
    soup = BeautifulSoup(body, "html.parser")
    statement = ""
    for article in soup.find_all("article"):
        for p in article.find_all(recursive=False):
            statement += p.get_text() + "\n\n"
    statement = "\n".join("\n".join(wrap(line, width=100)) for line in statement.strip().split("\n"))

    ans_re = re.compile("Your puzzle answer was")
    pt1, pt2 = None, None
    match [ans.next_element.get_text() for ans in soup.find_all(string=ans_re)]:
        case [spt1, spt2]:
            pt1, pt2 = spt1, spt2
        case [spt1]:
            pt1 = spt1
        case []:
            pass

    return statement, pt1, pt2


def _groupby(rows: Iterable, key: str) -> dict[Any, Any]:
    ret: dict[Any, Any] = {}
    for row in rows:
        ret.setdefault(getattr(row, key), []).append(row)
    return ret


def _count_stars(rows: Iterable) -> dict[int, dict[int, int]]:
    return {
        year: {
            day: 0 if s.pt1_answer is None else 1 if s.pt2_answer is None else 2
            for day, [s] in _groupby(rows, "day").items()
        }
        for year, rows in _groupby(rows, "year").items()
    }


def _years_summary(db: ElvenCrisisArchive, _cwd: Path) -> dict[int, str]:
    stats = db.ECASolution.fetch_all()
    year_stars = _count_stars(stats)

    ret = {}
    for year, days in year_stars.items():
        days_str = " ".join([f"{pad_day(day)}" for day in range(1, 26)])
        stars_str = " ".join([f"{'*' * days.get(day, 0):<2}" for day in range(1, 26)])
        summary = f"{stars_str}\n{days_str}"
        ret[year] = summary
    return ret


def _copy_boilerplate(_lang: LangSpec, _year: int, _day: int):
    pass
