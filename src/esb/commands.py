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
import shutil
from html.parser import HTMLParser
from itertools import product
from os import environ
from pathlib import Path
from textwrap import wrap

from esb.paths import input_path, statement_path

PACKAGE_ROOT = Path(__file__).parent
BLANK_ROOT = PACKAGE_ROOT.parent / "blank"


###########################################################
# Decorators
###########################################################
def is_esb_repo(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    # @TODO
    return wrapper


###########################################################
# Commands
###########################################################
def new():
    cwd = Path.cwd()
    for item in BLANK_ROOT.iterdir():
        if item.is_dir():
            shutil.copytree(item, cwd / item.name)
        else:
            shutil.copy(item, cwd)


@is_esb_repo
def fetch(years: list[int], days: list[int]):
    for year, day in product(years, days):
        host = "adventofcode.com"
        cookie = _load_cookie()

        st_route = f"/{year}/day/{day}"
        st_html = _fetch_url(host, st_route, cookie)
        statement = _parse_body(st_html)
        st_file = statement_path(year, day)
        st_file.parent.mkdir(parents=True, exist_ok=True)
        st_file.write_text(statement)

        input_route = f"{st_route}/input"
        puzzle_input = _fetch_url(host, input_route, cookie)
        input_file = input_path(year, day)
        input_file.parent.mkdir(parents=True, exist_ok=True)
        input_file.write_text(puzzle_input)


###########################################################
# Helper functions
###########################################################
def _load_cookie() -> str:
    cwd = Path.cwd()
    sess_env = "AOC_SESSION_COOKIE"
    dotenv = cwd / ".env"
    if dotenv.is_file():
        with dotenv.open() as fp:
            match [line.split("=")[1] for line in fp.read().split("\n") if line.startswith(sess_env)]:
                case [dot_cookie]:
                    return dot_cookie
    env_cookie: str | None = environ.get(sess_env)
    match env_cookie:
        case None:
            message = f"Could not find {sess_env}"
            raise ValueError(message)
        case str(_):
            return env_cookie


def _fetch_url(host: str, route: str, cookie: str) -> str:
    conn = http.client.HTTPSConnection(host)
    conn.request("GET", route, headers={"Cookie": f"session={cookie}"})
    res = conn.getresponse()
    # print(res)
    # print(res.status)
    # print(res.read().decode("utf-8"))
    # print(host, route)
    http_ok = 200
    if res.status != http_ok:
        message = "Could not fetch! Maybe your cookie have expired"
        raise ValueError(message)
    return res.read().decode("utf-8")


def _parse_body(body: str) -> str:
    class AoCHTMLParser(HTMLParser):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.tags = []
            self.text = ""

        def handle_starttag(self, tag, attrs):
            self.tags.append(tag)
            if tag == "p":
                self.text += "\n"

        def handle_endtag(self, tag):
            self.tags.pop()

        def handle_data(self, data):
            if "article" in self.tags:
                self.text += data

    p = AoCHTMLParser()
    p.feed(body)
    description_pt1 = p.text.strip()
    return "\n".join("\n".join(wrap(line, width=100)) for line in description_pt1.split("\n"))
