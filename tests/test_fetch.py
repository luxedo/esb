"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from pathlib import Path
from unittest.mock import patch

from esb.fetch import RudolphFetcher, RudolphSubmitStatus
from tests.lib.temporary import TestWithInitializedEsbRepo

ROOT_DIR = Path(__file__).parent
MOCK_DIR = ROOT_DIR / "mock"
TEST_STATEMENT = (MOCK_DIR / "statement.html").read_text()
TEST_SUBMIT_SUCCESS = (MOCK_DIR / "submit_success.html").read_text()
TEST_SUBMIT_FAIL = (MOCK_DIR / "submit_fail.html").read_text()
TEST_SUBMIT_TIMEOUT = (MOCK_DIR / "submit_timeout.html").read_text()
TEST_SUBMIT_ALREADY_SOLVED = (MOCK_DIR / "submit_already_complete.html").read_text()
HTTP_POST = "esb.fetch.RudolphFetcher.http_post"


class TestRudolphFetcher(TestWithInitializedEsbRepo):
    TEST_YEAR = 2020
    TEST_DAY = 1

    def test_fetch_submit_success(self):
        rf = RudolphFetcher(self.repo_root)
        with patch(HTTP_POST, return_value=TEST_SUBMIT_SUCCESS):
            submit_status = rf.fetch_submit(self.TEST_YEAR, self.TEST_DAY, 1, "Any")
        assert submit_status == RudolphSubmitStatus.SUCCESS

    def test_fetch_submit_fail(self):
        rf = RudolphFetcher(self.repo_root)
        with patch(HTTP_POST, return_value=TEST_SUBMIT_FAIL):
            submit_status = rf.fetch_submit(self.TEST_YEAR, self.TEST_DAY, 1, "Any")
        assert submit_status == RudolphSubmitStatus.FAIL

    def test_fetch_submit_timeout(self):
        rf = RudolphFetcher(self.repo_root)
        with patch(HTTP_POST, return_value=TEST_SUBMIT_TIMEOUT):
            submit_status = rf.fetch_submit(self.TEST_YEAR, self.TEST_DAY, 1, "Any")
        assert submit_status == RudolphSubmitStatus.TIMEOUT

    def test_fetch_submit_already_complete(self):
        rf = RudolphFetcher(self.repo_root)
        with patch(HTTP_POST, return_value=TEST_SUBMIT_ALREADY_SOLVED):
            submit_status = rf.fetch_submit(self.TEST_YEAR, self.TEST_DAY, 1, "Any")
        assert submit_status == RudolphSubmitStatus.ALREADY_COMPLETE
