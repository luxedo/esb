"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

import io
import os
import unittest
from collections.abc import Iterable
from itertools import cycle
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from esb.db import ElvenCrisisArchive
from esb.fetch import RudolphFetcher


class TestWithTemporaryDirectory(unittest.TestCase):
    current_dir: Path
    tmp_dir: TemporaryDirectory

    def setUp(self):
        self.current_dir = Path.cwd()
        self.tmp_dir = TemporaryDirectory()
        os.chdir(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()
        os.chdir(self.current_dir)


class TestWithInitializedEsbRepo(TestWithTemporaryDirectory):
    repo_root: Path

    def setUp(self):
        super().setUp()
        self.repo_root = Path.cwd()
        # Creates the db file
        # This is the condition for a directory to be considered an esb repository
        ElvenCrisisArchive(self.repo_root).new_repo()


class HttpMock:
    http_response: list[str]
    responses: Iterable[str]

    def __init__(self, http_response: list[str]):
        self.http_response = http_response
        self.next_response = cycle(self.http_response)

    def __enter__(self):
        self.stderr = io.StringIO()
        self.stdout = io.StringIO()
        self.patchers = [
            patch("esb.fetch.RudolphFetcher.http_get", side_effect=self.next_response),
            patch("esb.fetch.RudolphFetcher.http_post", side_effect=self.next_response),
            patch.dict(os.environ, {RudolphFetcher.sess_env: "mocka moccha"}),
        ]

        for patcher in self.patchers:
            patcher.start()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for patcher in reversed(self.patchers):
            patcher.stop()


class CliMock(HttpMock):
    command: list[str]
    http_response: list[str]
    stderr: io.StringIO
    stdout: io.StringIO

    def __init__(self, command: list[str], http_response: list[str] | None = None):
        if http_response is None:
            http_response = [""]
        super().__init__(http_response)
        self.command = command

    def __enter__(self):
        super().__enter__()

        self.stderr = io.StringIO()
        self.stdout = io.StringIO()
        new_patchers = [
            patch("sys.argv", self.command),
            patch("sys.stderr", new_callable=lambda: self.stderr),
            patch("sys.stdout", new_callable=lambda: self.stdout),
        ]

        self.patchers = [*self.patchers, *new_patchers]

        for patcher in new_patchers:
            patcher.start()

        return self
