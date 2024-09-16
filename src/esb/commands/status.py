"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from __future__ import annotations

from esb.commands.base import Command, oprint_info
from esb.lib.dash import CliDash


class Status(Command):
    full: bool
    esb_repo: bool = True

    def __init__(self, *, full: bool = False):
        super().__init__()
        self.full = full

    def execute(self):
        cli_dash = CliDash(self.db, self.lang_map, full=self.full)
        oprint_info(cli_dash.build_dash())
