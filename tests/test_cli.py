"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).


Copyright (C) 2024 Luiz Eduardo Amaral <luizamaral306@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import unittest
from argparse import Namespace
from unittest.mock import patch

import pytest

from esb.__main__ import main
from esb.cli import esb_parser


class TestEsbParser(unittest.TestCase):
    def setUp(self):
        self.parser = esb_parser()

    def test_working_commands(self):
        commands = [
            "esb init",
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
            "esb fetch --year 2014 --day 9",
            "esb fetch --year 2016 --day 40",
            "esb wrong_command",
        ]
        for command in commands:
            [_, *args] = command.split()
            with self.subTest(command=f"Non working command: {command}"), pytest.raises(SystemExit):
                self.parser.parse_args(args)


class TestCli(unittest.TestCase):
    def test_fetch(self):
        command = "esb fetch --year 2016 --day 9"
        with patch("sys.argv", command.split()):
            main()
            # captured = sys.stdout
            # print(captured.read())
