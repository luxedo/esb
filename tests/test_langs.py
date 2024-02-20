"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from esb.langs import LangMap
from tests.lib.temporary import TestWithInitializedEsbRepo


class TestLangs(TestWithInitializedEsbRepo):
    def test_build_command(self):
        lmap = LangMap.load_defaults()
        lang = lmap.get("python")
        year = 2021
        day = 10
        cmd = " ".join(lang.build_command(year, day))
        assert "python" in cmd
        assert str(year) in cmd
        assert str(day) in cmd
