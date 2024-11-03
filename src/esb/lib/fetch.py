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
from enum import Enum, auto
from os import environ
from textwrap import wrap
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from esb import __version__
from esb.lib.paths import pad_day

if TYPE_CHECKING:
    from pathlib import Path

    from bs4 import Tag

    from esb.protocol.fireplace import FPPart


class RudolphSubmitStatus(Enum):
    SUCCESS = auto()
    FAIL = auto()
    TIMEOUT = auto()
    ALREADY_COMPLETE = auto()
    ERROR = auto()


class RudolphFetcher:
    repo_root: Path
    cookie: str
    sess_env = "AOC_SESSION_COOKIE"
    host = "adventofcode.com"
    st_route = "/{year}/day/{day}"
    in_route = "{st_route}/input"  # noqa: RUF027
    ans_route = "{st_route}/answer"  # noqa: RUF027
    test_host = "raw.githubusercontent.com"
    test_route = "/luxedo/esb/main/aoc_tests/{year}/{day}/tests_{year}_{day}.toml"
    http_ok = 200

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.cookie = self.load_cookie(repo_root)

    @classmethod
    def load_cookie(cls, repo_root) -> str:
        dotenv = repo_root / ".env"
        if dotenv.is_file():
            with dotenv.open() as fp:
                [dot_cookie] = [line.split("=")[1] for line in fp.read().split("\n") if line.startswith(cls.sess_env)]
                return dot_cookie.removeprefix('"').removesuffix('"')
        env_cookie: str | None = environ.get(cls.sess_env)
        match env_cookie:
            case None:
                message = f"Could not find {cls.sess_env}"
                raise ValueError(message)
            case str(_):
                return env_cookie

    @staticmethod
    def request(
        host: str, route: str, method: str, headers: dict | None = None, data: dict | None = None
    ) -> http.client.HTTPResponse:
        conn = http.client.HTTPSConnection(host)
        conn.request(
            method,
            route,
            body=None if data is None else urlencode(data).encode("utf-8"),
            headers={} if headers is None else headers,
        )
        return conn.getresponse()

    def aoc_get(self, host: str, route: str) -> str:
        headers = {
            "Cookie": f"session={self.cookie}",
            "User-Agent": f"ElfScipt Brigade/{__version__}; github.com/luxedo/esb by luizamaral306@gmail.com",
        }
        res = self.request(host, route, "GET", headers)
        if res.status != self.http_ok:
            message = "Could not fetch! Maybe your cookie have expired"
            raise ValueError(message)
        return res.read().decode("utf-8")

    def aoc_post(self, host: str, route: str, form_data: dict) -> str:
        headers = {
            "Cookie": f"session={self.cookie}",
            "User-Agent": f"ElfScipt Brigade/{__version__}; github.com/luxedo/esb by luizamaral306@gmail.com",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        res = self.request(host, route, "POST", headers, form_data)
        if res.status != self.http_ok:
            message = "Could not post! Maybe your cookie have expired"
            raise ValueError(message)
        return res.read().decode("utf-8")

    def get_text(self, element: Tag):
        text = ""
        if element.name:
            if element.name in {"p", "pre"}:
                text += "\n\n"
            for child in element.children:
                text += self.get_text(child)  # type: ignore
        else:
            text += element.text
        return text

    def fetch_statement(self, year: int, day: int) -> tuple[str, str, str | None, str | None]:
        route = self.st_route.format(year=year, day=day)
        body = self.aoc_get(self.host, route)

        soup = BeautifulSoup(body, "html.parser")
        statement = ""
        for article in soup.find_all("article"):
            statement += "\n"
            statement += self.get_text(article)
        statement = re.sub(r"\n{3,}", "\n\n", statement)
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
        return self.aoc_get(self.host, route)

    def fetch_submit(self, year: int, day: int, part: FPPart, answer: str) -> RudolphSubmitStatus:
        ans_route = self.ans_route.format(st_route=self.st_route.format(year=year, day=day))
        body = self.aoc_post(self.host, ans_route, form_data={"level": part, "answer": answer})
        soup = BeautifulSoup(body, "html.parser")
        matches = {
            RudolphSubmitStatus.SUCCESS: "That's the right answer!",
            RudolphSubmitStatus.FAIL: "That's not the right answer",
            RudolphSubmitStatus.TIMEOUT: "You gave an answer too recently",
            RudolphSubmitStatus.ALREADY_COMPLETE: "Did you already complete it?",
        }

        def match_substr(substr):
            return lambda tag: (
                tag is not None
                and tag.name == "p"
                and tag.parent is not None
                and tag.parent.name == "article"
                and substr in tag.getText()
            )

        for ret, substr in matches.items():
            if soup.find(match_substr(substr)) is not None:
                return ret
        return RudolphSubmitStatus.ERROR

    def fetch_tests(self, year: int, day: int) -> str:
        route = self.test_route.format(year=year, day=pad_day(day))
        res = self.request(self.test_host, route, "GET")
        if res.status != self.http_ok:
            message = "Could not fetch tests :("
            raise ValueError(message)
        return res.read().decode("utf-8")
