"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from pathlib import Path

import pytest

from esb import db
from tests.lib.sql import reset_sql_connection
from tests.lib.temporary import TestWithTemporaryDirectory


class TestSqlConnection(TestWithTemporaryDirectory):
    @reset_sql_connection
    def test_singleton(self):
        db_path0 = "my_test0.db"
        sql0 = db.SqlConnection(db_path0)  # First one locks the database file
        sql1 = db.SqlConnection()  # Second one is just the singleton
        assert id(sql0) == id(sql1)
        [p] = list(Path.cwd().iterdir())
        assert p.name == db_path0

    @reset_sql_connection
    def test_cannot_change_db_at_runtime(self):
        db_path0 = "my_test0.db"
        db_path1 = "my_test1.db"
        _sql0 = db.SqlConnection(db_path0)  # First one locks the database file
        with pytest.raises(ValueError, match="Cannot change db_path after initialization"):
            _sql1 = db.SqlConnection(db_path1)  # First one locks the database file

    @reset_sql_connection
    def test_cannot_initialize_without_db_path_argument(self):
        with pytest.raises(TypeError):
            _sql0 = db.SqlConnection()  # First one locks the database file
