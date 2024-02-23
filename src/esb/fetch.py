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
from os import environ
from textwrap import wrap
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup

from esb import __version__

if TYPE_CHECKING:
    from pathlib import Path


class RudolphFetcher:
    repo_root: Path
    cookie: str
    sess_env = "AOC_SESSION_COOKIE"
    host = "adventofcode.com"
    st_route = "/{year}/day/{day}"
    in_route = "{st_route}/input"

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.cookie = self.load_cookie()

    def load_cookie(self) -> str:
        dotenv = self.repo_root / ".env"
        if dotenv.is_file():
            with dotenv.open() as fp:
                match [line.split("=")[1] for line in fp.read().split("\n") if line.startswith(self.sess_env)]:
                    case [dot_cookie]:
                        return dot_cookie.removeprefix('"').removesuffix('"')
        env_cookie: str | None = environ.get(self.sess_env)
        match env_cookie:
            case None:
                message = f"Could not find {self.sess_env}"
                raise ValueError(message)
            case str(_):
                return env_cookie

    def fetch_url(self, host: str, route: str) -> str:
        conn = http.client.HTTPSConnection(host)
        conn.request(
            "GET",
            route,
            headers={
                "Cookie": f"session={self.cookie}",
                "User-Agent": f"ElfScipt Brigade/{__version__}; github.com/luxedo/esb by luizamaral306@gmail.com",
            },
        )
        res = conn.getresponse()
        http_ok = 200
        if res.status != http_ok:
            message = "Could not fetch! Maybe your cookie have expired"
            raise ValueError(message)
        return res.read().decode("utf-8")

    def fetch_statement(self, year: int, day: int) -> tuple[str, str, str | None, str | None]:
        route = self.st_route.format(year=year, day=day)
        body = self.fetch_url(self.host, route)

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

        url = self.host + route
        return url, statement, pt1, pt2

    def fetch_input(self, year: int, day: int) -> str:
        route = self.in_route.format(st_route=self.st_route.format(year=year, day=day))
        return self.fetch_url(self.host, route)
