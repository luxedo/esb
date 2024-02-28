"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from pathlib import Path

MOCK_ROOT = Path(__file__).parent

SOLUTION_PYTHON = MOCK_ROOT / "solution.py"

STATEMENT_HTML = MOCK_ROOT / "statement.html"
SUBMIT_ALREADY_COMPLETE_HTML = MOCK_ROOT / "submit_already_complete.html"
SUBMIT_FAIL = MOCK_ROOT / "submit_fail.html"
SUBMIT_SUCCESS = MOCK_ROOT / "submit_success.html"
SUBMIT_TIMEOUT = MOCK_ROOT / "submit_timeout.html"

TESTS_SUCCESS_TOML = MOCK_ROOT / "tests_success.toml"
TESTS_ERROR_TOML = MOCK_ROOT / "tests_error.toml"
TESTS_MISSING_TOML = MOCK_ROOT / "tests_missing.toml"
