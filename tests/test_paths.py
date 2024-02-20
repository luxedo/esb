"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

import pytest

from esb import paths
from esb.langs import LangMap
from tests.lib.temporary import TestWithInitializedEsbRepo


class TestPaths(TestWithInitializedEsbRepo):
    def test_cachesled_getitem(self):
        cache_sled = paths.CacheSled()
        assert str(cache_sled.path("statement", year=2016, day=24)).endswith(".cache/2016/24/day_24_statement.txt")

    def test_cachesled_getitem_missing_key(self):
        cache_sled = paths.CacheSled()
        with pytest.raises(KeyError, match="Could not find path for file"):
            cache_sled.path(file="missing key", year=2016, day=24)

    def test_langsled_getitem(self):
        p = LangMap.load_defaults().get("python")
        lang_sled = paths.LangSled(name=p.name, files=p.files)
        assert str(lang_sled.path(file="main.py", year=2016, day=24)).endswith("python/2016/24/aoc_2016_24.py")

    def test_langsled_boiler_map(self):
        p = LangMap.load_defaults().get("python")
        lang_sled = paths.LangSled(name=p.name, files=p.files)
        for src, dst in lang_sled.boiler_map(year=2016, day=24).items():
            assert src.is_file()
            assert "python/2016/24/" in str(dst)
