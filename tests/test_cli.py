"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

import os
import unittest
from argparse import ArgumentTypeError, Namespace
from pathlib import Path

import pytest

from esb.cli import aoc_day, aoc_year, esb_parser, main
from esb.langs import LangMap
from esb.paths import CacheInputSled, LangSled
from tests.lib import CliMock, TestWithInitializedEsbRepo, TestWithTemporaryDirectory
from tests.mock import STATEMENT_HTML


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
            "esb test --year 2016 --day 9 --lang python -p 1",
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
            with self.subTest(command=f"Non working command: {command}"), pytest.raises(SystemExit, match="2"):
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

    TEST_YEAR = 2020
    TEST_DAY = 9

    cmd_new = "esb new".split()
    cmd_fetch = f"esb fetch --year {TEST_YEAR} --day {TEST_DAY}".split()
    language_name = "python"
    cmd_start = f"esb start --year {TEST_YEAR} --day {TEST_DAY} --lang {language_name}".split()
    cmd_show = f"esb show --year {TEST_YEAR} --day {TEST_DAY}".split()
    cmd_status = "esb status".split()
    cmd_dashboard = "esb dashboard".split()

    def esb_new(self):
        with CliMock(self.cmd_new, ""):
            main()

    def esb_fetch(self):
        with CliMock(self.cmd_fetch, STATEMENT_HTML.read_text()):
            main()

    def test_new(self):
        command = self.cmd_new
        with CliMock(command) as clim:
            main()
        text = clim.stderr.getvalue()
        assert "Thank you for saving Christmas" in text

    def test_new_must_fail_when_runing_in_an_esb_repo(self):
        self.esb_new()
        command = self.cmd_new
        with CliMock(command) as clim, pytest.raises(SystemExit, match="1"):
            main()
        text = clim.stderr.getvalue()
        assert "Cannot initialize" in text

    def test_fetch(self):
        self.esb_new()

        repo_root = Path.cwd()
        cs = CacheInputSled(repo_root)
        statement_file = cs.path("statement", self.TEST_YEAR, self.TEST_DAY)
        input_file = cs.path("input", self.TEST_YEAR, self.TEST_DAY)
        assert not statement_file.is_file()
        assert not input_file.is_file()

        command = self.cmd_fetch
        http_response = STATEMENT_HTML.read_text()
        with CliMock(command, http_response) as clim:
            main()
        text = clim.stderr.getvalue()
        assert "Fetched year" in text
        assert statement_file.is_file()
        assert input_file.is_file()

    def test_start(self):
        self.esb_new()
        command = self.cmd_start
        http_response = STATEMENT_HTML.read_text()
        with CliMock(command, http_response) as clim:
            main()
        text = clim.stderr.getvalue()
        assert "Started code for" in text, text

        lmap = LangMap.load_defaults()
        lang = lmap.get(self.language_name)
        lang_sled = LangSled.from_spec(repo_root=Path.cwd(), spec=lang)
        for dst in lang_sled.copied_map(self.TEST_YEAR, self.TEST_DAY).values():
            assert dst.is_file()

    def test_show(self):
        self.esb_new()
        self.esb_fetch()
        command = self.cmd_show
        http_response = STATEMENT_HTML.read_text()
        with CliMock(command, http_response) as clim:
            main()
        text = clim.stdout.getvalue()
        assert "Solution pt1" in text, text

    def test_status(self):
        self.esb_new()

        command = self.cmd_status
        with CliMock(command) as clim:
            main()
        text = clim.stdout.getvalue()
        assert "ELFSCRIPT BRIGADE STATUS REPORT" in text

    def test_status_runs_in_any_esb_repo_subdir(self):
        self.esb_new()

        dir_name = "test_dir"
        Path(dir_name).mkdir()
        os.chdir(dir_name)

        command = self.cmd_status
        with CliMock(command) as clim:
            main()
        text = clim.stdout.getvalue()
        assert "ELFSCRIPT BRIGADE STATUS REPORT" in text

    def test_status_should_fail_when_running_not_in_an_esb_repo(self):
        command = self.cmd_status
        with CliMock(command) as clim, pytest.raises(SystemExit, match="2"):
            main()
        text = clim.stderr.getvalue()
        assert "Fatal: this is not an ElfScript Brigade repo" in text

    def test_dashboard(self):
        self.esb_new()

        command = self.cmd_dashboard
        with CliMock(command) as clim:
            main()
        text = clim.stdout.getvalue()
        assert "Dashboard rebuilt successfully!" in text
