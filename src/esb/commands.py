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
from esb.db import ElvenCrisisArchive
from esb.paths import BLANK_ROOT, CachePaths, LangPaths, pad_day
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

    db.BrigadistaInfo(brigadista_id=str(uuid.uuid4()), creation_date=datetime.now().astimezone()).insert()

    console_err.print(
        "ESB repo is ready! Thank you for saving Christmas [italic]Elf[/italic]",
        style=COLOR_INFO,
    )


@is_esb_repo
def fetch(years: list[int], days: list[int], *, force: bool = False):
    db = ElvenCrisisArchive()
    cwd = Path.cwd()
    for year, day in product(years, days):
        ds = db.SolutionStatus.find_single({"year": year, "day": day})
        if not force and ds is not None and ds.pt2_answer is not None:
            console_err.print(
                f"Fetch for year {year} day {pad_day(day)} is already complete!",
                style=COLOR_INFO,
            )
            continue

        host = "adventofcode.com"
        cookie = _load_cookie()

        st_route = f"/{year}/day/{day}"
        st_html = _fetch_url(host, st_route, cookie)
        statement, pt1_answer, pt2_answer = _parse_body(st_html)
        st_file = CachePaths(cwd).statement_path(year, day)
        st_file.parent.mkdir(parents=True, exist_ok=True)
        st_file.write_text(statement)

        db.SolutionStatus(year=year, day=day, pt1_answer=pt1_answer, pt2_answer=pt2_answer).insert(replace=True)

        input_file = CachePaths(cwd).input_path(year, day)
        if not force and input_file.is_file():
            console_err.print(
                f"Input for year {year} day {pad_day(day)} already cached",
                style=COLOR_INFO,
            )
            continue
        input_route = f"{st_route}/input"
        puzzle_input = _fetch_url(host, input_route, cookie)
        input_file.parent.mkdir(parents=True, exist_ok=True)
        input_file.write_text(puzzle_input)
        console_err.print(
            f"Fetched year {year} day {pad_day(day)}!",
            style=COLOR_INFO,
        )


@is_esb_repo
def start(lang: LangSpec, years: list[int], days: list[int]):
    # db = ElvenCrisisArchive()
    for year, day in product(years, days):
        start_day(lang, year, day)


def start_day(lang: LangSpec, year: int, day: int):
    _copy_boilerplate(lang, year, day)


@is_esb_repo
def show(years: list[int], days: list[int]):
    db = ElvenCrisisArchive()
    for year, day in product(years, days):
        show_day(db, year, day)


def show_day(db: ElvenCrisisArchive, year: int, day: int):
    ds = db.SolutionStatus.find_single({"year": year, "day": day})
    cwd = Path.cwd()
    statement_file = CachePaths(cwd).statement_path(year, day)
    if ds is None or not statement_file.is_file():
        console_err.print(
            f"Input for year {year} day {pad_day(day)} not cached. Please fetch first",
            style=COLOR_ERROR,
        )
        return

    not_solved = "<Not solved yet>"
    console_out.print(statement_file.read_text())
    console_out.print()
    console_out.print(f"Solution pt1: {ds.pt1_answer or not_solved}")
    console_out.print(f"console_out pt2: {ds.pt2_answer or not_solved}")


@is_esb_repo
def status():
    db = ElvenCrisisArchive()
    info = db.BrigadistaInfo.fetch_single()
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
    cwd = Path.cwd()
    db = ElvenCrisisArchive()
    for year, day in product(years, days):
        ds = db.SolutionStatus.find_single({"year": year, "day": day})
        if ds is None:
            console_err.print(
                f"Could not find input for year {year} day {pad_day(day)}. Please fetch first.",
                style=COLOR_ERROR,
            )

        day_input = CachePaths(cwd).input_path(year, day)
        day_wd = LangPaths(cwd).day_source(lang, year, day)  # @TODO: Chose working directory according with LangSpec
        command = [*lang.command, lang.source(year, day)]
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
                sys.exit(2)
            case fp1_0.FPStatus.ProtocolError:
                console_err.print(
                    f"\nSolution for year {year} day {pad_day(day)} does not follow FIREPLACE protocol.",
                    style=COLOR_ERROR,
                )
                sys.exit(2)

        attempt = result.answer
        answer = ds.get_answer(part)
        if answer is not None:
            if attempt == answer:
                console_out.print(f"✔ Answer pt{part}: {attempt}", style=COLOR_INFO)
            else:
                console_out.print(
                    f"✘ Answer pt{part}: {attempt}. Expected: {answer}",
                    style=COLOR_ERROR,
                )
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
    stats = db.SolutionStatus.fetch_all()
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
