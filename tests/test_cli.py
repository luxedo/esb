"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

import os
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

import pytest

from esb.cli import esb_parser, main
from esb.commands import new
from esb.paths import input_path, statement_path

ROOT_DIR = Path(__file__).parent


class TestEsbParser(unittest.TestCase):
    def setUp(self):
        self.parser = esb_parser()

    def test_working_commands(self):
        commands = [
            "esb new",
            "esb fetch --year 2016 --day 9",
            "esb test --all",
            "esb test --year 2016 --day 9 --lang python --all",
            "esb run --all",
            "esb run --year 2016 --day 9 --lang python",
            "esb run --year 2016 --day 9 --lang python",
            "esb run --year 2016 --day 9 --lang python --submit",
            "esb run -y 2016 -d 9 -l python -s",
            "esb dashboard",
        ]
        for command in commands:
            [_, *args] = command.split()
            with self.subTest(command=f"Working command: {command}"):
                args = self.parser.parse_args(args)
                assert isinstance(args, Namespace)

    def test_non_working_commands(self):
        commands = [
            "esb new --year 2014",
            "esb fetch --year 2014 --day 9",
            "esb fetch --year 2016 --day 40",
            "esb wrong_command",
        ]
        for command in commands:
            [_, *args] = command.split()
            with self.subTest(command=f"Non working command: {command}"), pytest.raises(SystemExit):
                self.parser.parse_args(args)


class TestCli(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        os.chdir(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()


class TestCliNew(TestCli):
    def test_new(self):
        command = "esb new"

        with patch("sys.argv", command.split()):
            main()


class TestCliFetch(TestCli):
    TEST_EXAMPLE_STATEMENT = (ROOT_DIR / "mock" / "example.html").read_text()
    TEST_YEAR = 2020
    TEST_DAY = 9

    @patch("esb.commands._fetch_url", return_value=TEST_EXAMPLE_STATEMENT)
    # @pytest.mark.usefixtures("mock_fetch_url")
    def test_fetch(self, mock_fetch_url):
        new()

        statement_file = statement_path(self.TEST_YEAR, self.TEST_DAY)
        input_file = input_path(self.TEST_YEAR, self.TEST_DAY)
        assert not statement_file.is_file()
        assert not input_file.is_file()

        command = f"esb fetch --year {self.TEST_YEAR} --day {self.TEST_DAY}"
        with patch("sys.argv", command.split()):
            main()

        assert mock_fetch_url.called
        assert statement_file.is_file()
        assert input_file.is_file()
