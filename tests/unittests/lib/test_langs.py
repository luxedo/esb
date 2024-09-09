"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

import unittest

from esb.config import ESBConfig
from esb.lib.langs import LangMap, LangSpec


class TestLangSpec(unittest.TestCase):
    def test_from_json(self):
        lang_name = "python"
        LangSpec.from_json(ESBConfig.boiler_root / lang_name / ESBConfig.spec_filename)


class TestLangMap(unittest.TestCase):
    def test_from_defaults(self):
        lang_name = "python"
        lang_map = LangMap.load_defaults()
        assert lang_name in lang_map.names
