"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from __future__ import annotations

from esb.commands.base import Command, oprint_error, oprint_info
from esb.lib.dash import MdDash


class Dashboard(Command):
    reset: bool
    esb_repo: bool = True

    def __init__(self, *, reset: bool = False):
        super().__init__()
        self.reset = reset

    def execute(self):
        md_dash = MdDash(self.db, self.lang_map, self.repo_root)
        md_dash.build_dash(reset=self.reset)
        md_dash.build_report(reset=self.reset)
        try:
            md_dash.build_dash(reset=self.reset)
            md_dash.build_report(reset=self.reset)
            oprint_info("Dashboard rebuilt successfully!")
        except ValueError:
            oprint_error("Error building dashboard. Check if you have all the needed tags in the template")
