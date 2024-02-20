"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

import io
import unittest
from argparse import ArgumentTypeError, Namespace
from pathlib import Path
from unittest.mock import patch

import pytest

from esb.cli import aoc_day, aoc_year, esb_parser, main
from esb.langs import LangMap
from esb.paths import CacheSled
from tests.lib.temporary import TestWithInitializedEsbRepo, TestWithTemporaryDirectory

ROOT_DIR = Path(__file__).parent


class TestParserTypes(unittest.TestCase):
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


class TestEsbParser(TestWithInitializedEsbRepo):
    def test_working_commands(self):
        commands = [
            "esb new",
            "esb fetch --year 2016 --day 9",
            "esb start --lang python --year 2016 --day 9",
            "esb test --year 2016 --day 9 --lang python",
            "esb run --year 2016 --day 9 --lang python --part 1",
            "esb run --year 2016 --day 9 --lang python -p 2",
            "esb run --year 2016 --day 9 --lang python -p 1 --submit",
            "esb run -y 2016 -d 9 -l python -s --part 2",
            "esb dashboard",
        ]
        self.parser = esb_parser()
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
            "esb run --year 2016 --day 9",
        ]
        self.parser = esb_parser()
        for command in commands:
            [_, *args] = command.split()
            with self.subTest(command=f"Non working command: {command}"), pytest.raises(SystemExit):
                self.parser.parse_args(args)


class TestCli(TestWithTemporaryDirectory):
    """
    Commands:

    new
    fetch
    start
    show
    status
    test
    run
    dashboard
    """

    TEST_EXAMPLE_STATEMENT = (ROOT_DIR / "mock" / "example.html").read_text()
    TEST_YEAR = 2020
    TEST_DAY = 9

    @patch("sys.stderr", new_callable=io.StringIO)
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_new(self, _stderr, stdout):  # noqa: PT019
        command = "esb new"

        with patch("sys.argv", command.split()):
            main()

        text = stdout.getvalue()
        assert "Thank you for saving Christmas" in text, text

    @patch("esb.commands._fetch_url", return_value=TEST_EXAMPLE_STATEMENT)
    @patch("sys.stderr", new_callable=io.StringIO)
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_fetch(self, stdout, _stderr, mock_fetch_url):  # noqa: PT019
        command = "esb new"
        with patch("sys.argv", command.split()):
            main()

        cs = CacheSled()
        statement_file = cs.path("statement", self.TEST_YEAR, self.TEST_DAY)
        input_file = cs.path("input", self.TEST_YEAR, self.TEST_DAY)
        assert not statement_file.is_file()
        assert not input_file.is_file()

        command = f"esb fetch --year {self.TEST_YEAR} --day {self.TEST_DAY}"
        with patch("sys.argv", command.split()):
            main()

        assert mock_fetch_url.called
        assert statement_file.is_file()
        assert input_file.is_file()

    @patch("esb.commands._fetch_url", return_value=TEST_EXAMPLE_STATEMENT)
    @patch("sys.stderr", new_callable=io.StringIO)
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_start(self, _, _stderr, stdout):  # noqa: PT019
        command = "esb new"
        with patch("sys.argv", command.split()):
            main()

        language_name = "python"
        command = f"esb start --year {self.TEST_YEAR} --day {self.TEST_DAY} --lang {language_name}"
        with patch("sys.argv", command.split()):
            main()

        lmap = LangMap.load_defaults()
        lang = lmap.get(language_name)
        for dst in lang.sled.copied_map(self.TEST_YEAR, self.TEST_DAY).values():
            assert dst.is_file()

    @patch("esb.commands._fetch_url", return_value=TEST_EXAMPLE_STATEMENT)
    @patch("sys.stderr", new_callable=io.StringIO)
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_show(self, stdout, _stderr, _):  # noqa: PT019
        command = "esb new"
        with patch("sys.argv", command.split()):
            main()

        command = f"esb fetch --year {self.TEST_YEAR} --day {self.TEST_DAY}"
        with patch("sys.argv", command.split()):
            main()

        command = f"esb show --year {self.TEST_YEAR} --day {self.TEST_DAY}"
        with patch("sys.argv", command.split()):
            main()

        text = stdout.getvalue()
        assert "Solution pt1" in text

    @patch("esb.commands._fetch_url", return_value=TEST_EXAMPLE_STATEMENT)
    @patch("sys.stderr", new_callable=io.StringIO)
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_status(self, stdout, _stderr, _):  # noqa: PT019
        command = "esb new"
        with patch("sys.argv", command.split()):
            main()

        command = "esb status"
        with patch("sys.argv", command.split()):
            main()

        command = f"esb fetch --year {self.TEST_YEAR} --day {self.TEST_DAY}"
        with patch("sys.argv", command.split()):
            main()

        text = stdout.getvalue()
        assert "ELFSCRIPT BRIGADE STATUS REPORT" in text
