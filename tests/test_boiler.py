"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from pathlib import Path

from esb.boiler import CodeFurnace
from esb.langs import LangMap
from esb.paths import LangSled
from tests.lib import TestWithInitializedEsbRepo


class TestBoiler(TestWithInitializedEsbRepo):
    year = 2016
    day = 3
    title = "Example title"
    url = "https://my-url"
    lmap = LangMap.load_defaults()

    def load_lang_sled(self, lang_name: str) -> tuple[LangSled, LangMap]:
        lang_spec = self.lmap.get(lang_name)
        return LangSled(repo_root=Path.cwd(), name=lang_name, files=lang_spec.files), lang_spec

    def assert_files(self, lang_sled: LangSled):
        for dst in lang_sled.copied_map(self.year, self.day).values():
            assert dst.is_file()
            text = dst.read_text()
            assert str(self.year) in text
            assert str(self.day) in text
            assert self.title in text
            assert self.url in text

    def test_code_furnace_start(self):
        for lang_name in ["python", "rust"]:
            with self.subTest(lang_name=lang_name):
                lang_sled, lang_spec = self.load_lang_sled(lang_name)
                cf = CodeFurnace(lang_spec, lang_sled)
                cf.start(self.year, self.day, self.title, self.url)
                self.assert_files(lang_sled)

    def test_code_furnace_clear_dir(self):
        lang_name = "python"
        lang_sled, lang_spec = self.load_lang_sled(lang_name)

        cf = CodeFurnace(lang_spec, lang_sled)
        cf.start(self.year, self.day, self.title, self.url)
        test_file = lang_sled.day_dir(self.year, self.day) / "test.txt"
        test_file.touch()
        assert test_file.exists()

        # Run again. Should clean the directory
        cf.start(self.year, self.day, self.title, self.url)
        assert not test_file.exists()

        self.assert_files(lang_sled)
