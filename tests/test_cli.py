"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

import unittest
from argparse import ArgumentTypeError, Namespace
from pathlib import Path
from unittest.mock import patch

import pytest

from esb.cli import aoc_day, aoc_year, esb_parser, main
from esb.commands import new
from esb.paths import input_path, statement_path
from tests.lib.temporary import TestWithTemporaryDirectory

ROOT_DIR = Path(__file__).parent


class TestParserTypes(unittest.TestCase):
    # @TODO: Check this properly
    def test_aoc_day_single(self):
        for day in range(1, 26):
            with self.subTest(aoc_day=day):
                assert aoc_day(str(day)) == day

    def test_aoc_day_error(self):
        for day in [0, 26, "twenty-seven"]:
            with self.subTest(aoc_day=day, error=True), pytest.raises(
                ArgumentTypeError, match="is not a valid AoC day"
            ):
                aoc_day(str(day))

    def test_aoc_day_all(self):
        assert aoc_day("all") == range(1, 26)

    def test_aoc_year_single(self):
        for year in range(2015, 2024):
            with self.subTest(aoc_year=year):
                assert aoc_year(str(year)) == year

    def test_aoc_year_error(self):
        for year in [2014, 2031, "twenty-seven"]:
            with self.subTest(aoc_year=year, error=True), pytest.raises(
                ArgumentTypeError, match="is not a valid AoC year"
            ):
                aoc_year(str(year))

    def test_aoc_year_all(self):
        assert aoc_year("all") == range(2015, 2024)


class TestEsbParser(unittest.TestCase):
    def setUp(self):
        self.parser = esb_parser()

    def test_working_commands(self):
        commands = [
            "esb new",
            "esb fetch --year 2016 --day 9",
            "esb start --lang python --year 2016 --day 9",
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
            "esb start --year 2016 --day 9",
        ]
        for command in commands:
            [_, *args] = command.split()
            with self.subTest(command=f"Non working command: {command}"), pytest.raises(SystemExit):
                self.parser.parse_args(args)


class TestCliNew(TestWithTemporaryDirectory):
    def test_new(self):
        command = "esb new"

        with patch("sys.argv", command.split()):
            main()


class TestCliFetch(TestWithTemporaryDirectory):
    TEST_EXAMPLE_STATEMENT = (ROOT_DIR / "mock" / "example.html").read_text()
    TEST_YEAR = 2020
    TEST_DAY = 9

    @patch("esb.commands._fetch_url", return_value=TEST_EXAMPLE_STATEMENT)
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


# class TestCliStart(TestWithTemporaryDirectory):
#     TEST_EXAMPLE_STATEMENT = (ROOT_DIR / "mock" / "example.html").read_text()
#     TEST_YEAR = 2020
#     TEST_DAY = 9
#
#     @patch("esb.commands._fetch_url", return_value=TEST_EXAMPLE_STATEMENT)
#     def test_fetch(self, mock_fetch_url):
#         new()
#         # fetch([self.TEST_YEAR], [self.TEST_DAY])
#
#         # statement_file = statement_path(self.TEST_YEAR, self.TEST_DAY)
#         # input_file = input_path(self.TEST_YEAR, self.TEST_DAY)
#         # assert not statement_file.is_file()
#         # assert not input_file.is_file()
#
#         # command = f"esb fetch --year {self.TEST_YEAR} --day {self.TEST_DAY}"
#         # with patch("sys.argv", command.split()):
#         #     main()
#
#         # assert mock_fetch_url.called
#         # assert statement_file.is_file()
#         # assert input_file.is_file()
