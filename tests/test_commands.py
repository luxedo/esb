"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

import io
import shutil
import unittest
from unittest.mock import patch

from esb.commands.base import find_tests
from esb.commands.base import load_tests as esb_load_tests
from esb.paths import TestSled
from esb.protocol.fireplacev1_0 import FPPart
from tests.lib import TestWithInitializedEsbRepo
from tests.mock import TESTS_ERROR_TOML, TESTS_MISSING_TOML, TESTS_SUCCESS_TOML


class TestCommandsBaseLoadTests(unittest.TestCase):
    def test_load_tests_success(self):
        tests = esb_load_tests(TESTS_SUCCESS_TOML, 1)
        assert len(tests) == 4

        tests = esb_load_tests(TESTS_SUCCESS_TOML, 2)
        assert len(tests) == 3

    def test_load_tests_error(self):
        with patch("sys.stderr", new_callable=io.StringIO) as stderr:
            tests = esb_load_tests(TESTS_ERROR_TOML, 1)

        assert len(tests) == 0

        text = stderr.getvalue()
        assert "is malformed" in text

    def test_load_tests_missing(self):
        with patch("sys.stderr", new_callable=io.StringIO) as stderr:
            tests = esb_load_tests(TESTS_MISSING_TOML, 1)

        assert len(tests) == 1

        text = stderr.getvalue()
        assert "test_01_pt1 is missing" in text
        assert "test_02_pt1 is missing" in text
        assert "test_03_pt1 is missing" in text


class TestCommandsBaseFindTests(TestWithInitializedEsbRepo):
    year = 2019
    day = 10
    part: FPPart = 1

    def test_find_tests(self):
        ts = TestSled(self.repo_root)
        day_dir = ts.day_dir(self.year, self.day)
        day_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(TESTS_SUCCESS_TOML, day_dir)
        tests = find_tests(self.repo_root, self.year, self.day, self.part)
        assert len(tests) == 4

    def test_find_tests_with_empty_directory(self):
        with patch("sys.stderr", new_callable=io.StringIO) as stderr:
            tests = find_tests(self.repo_root, self.year, self.day, self.part)

        assert len(tests) == 0

        text = stderr.getvalue()
        assert "Could not find tests for year" in text
