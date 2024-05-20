"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from esb.fetch import RudolphFetcher, RudolphSubmitStatus
from tests.lib import HttpMock, TestWithInitializedEsbRepo
from tests.mock import SUBMIT_ALREADY_COMPLETE, SUBMIT_FAIL, SUBMIT_SUCCESS, SUBMIT_TIMEOUT


class TestRudolphFetcher(TestWithInitializedEsbRepo):
    TEST_YEAR = 2020
    TEST_DAY = 1

    def test_fetch_submit_success(self):
        with HttpMock([SUBMIT_SUCCESS.read_text()]):
            rf = RudolphFetcher(self.repo_root)
            submit_status = rf.fetch_submit(self.TEST_YEAR, self.TEST_DAY, 1, "Any")
        assert submit_status == RudolphSubmitStatus.SUCCESS

    def test_fetch_submit_fail(self):
        with HttpMock([SUBMIT_FAIL.read_text()]):
            rf = RudolphFetcher(self.repo_root)
            submit_status = rf.fetch_submit(self.TEST_YEAR, self.TEST_DAY, 1, "Any")
        assert submit_status == RudolphSubmitStatus.FAIL

    def test_fetch_submit_timeout(self):
        with HttpMock([SUBMIT_TIMEOUT.read_text()]):
            rf = RudolphFetcher(self.repo_root)
            submit_status = rf.fetch_submit(self.TEST_YEAR, self.TEST_DAY, 1, "Any")
        assert submit_status == RudolphSubmitStatus.TIMEOUT

    def test_fetch_submit_already_complete(self):
        with HttpMock([SUBMIT_ALREADY_COMPLETE.read_text()]):
            rf = RudolphFetcher(self.repo_root)
            submit_status = rf.fetch_submit(self.TEST_YEAR, self.TEST_DAY, 1, "Any")
        assert submit_status == RudolphSubmitStatus.ALREADY_COMPLETE
