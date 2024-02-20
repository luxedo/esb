"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from esb.boiler import CodeFurnace
from esb.langs import LangMap
from tests.lib.temporary import TestWithInitializedEsbRepo


class TestBoiler(TestWithInitializedEsbRepo):
    def test_code_furnace_start(self):
        lmap = LangMap.load_defaults()
        lang = lmap.get("python")
        cf = CodeFurnace(lang)
        year = 2016
        day = 3
        title = "Example title"
        url = "https://my-url"
        cf.start(year, day, title, url)
        for dst in lang.sled.copied_map(year, day).values():
            assert dst.is_file()
            text = dst.read_text()
            assert str(year) in text
            assert str(day) in text
            assert title in text
            assert url in text
