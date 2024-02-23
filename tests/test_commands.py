"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

import io
from pathlib import Path
from unittest.mock import patch

import pytest

from esb.commands import status
from esb.db import ElvenCrisisArchive
from tests.lib.temporary import TestWithTemporaryDirectory


class TestCommandWrappers(TestWithTemporaryDirectory):
    def test_is_esb_repo_should_raise_when_running_outside_an_esb_repo(self):
        with pytest.raises(SystemExit, match="2"), patch("sys.stderr", new_class=io.StringIO):
            status()

    def test_is_esb_repo_should_not_raise_when_running_inside_an_esb_repo(self):
        repo_root = Path.cwd()
        # Creates the db file
        # This is the condition for a directory to be considered an esb repository
        ElvenCrisisArchive(repo_root).new_repo()
        status()
