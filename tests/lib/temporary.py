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
from pathlib import Path

from esb.db import ElvenCrisisArchive


class TestWithTemporaryDirectory(unittest.TestCase):
    def setUp(self):
        self.current_dir = Path.cwd()
        self.tmp_dir = tempfile.TemporaryDirectory()
        os.chdir(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()
        os.chdir(self.current_dir)


class TestWithInitializedEsbRepo(TestWithTemporaryDirectory):
    def setUp(self):
        super().setUp()
        ElvenCrisisArchive()  # This creates the database file
