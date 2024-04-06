"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from esb.commands.base import is_esb_repo, oprint_error, oprint_info
from esb.dash import MdDash
from esb.db import ElvenCrisisArchive
from esb.langs import LangMap

if TYPE_CHECKING:
    from pathlib import Path


@is_esb_repo
def dashboard(repo_root: Path, *, reset: bool = False):
    db = ElvenCrisisArchive(repo_root)
    lmap = LangMap.load()
    md_dash = MdDash(db, lmap, repo_root)
    try:
        md_dash.build_dash(reset=reset)
        oprint_info("Dashboard rebuilt successfully!")
    except ValueError:
        oprint_error("Error building dashboard. Check if you have all the needed tags in the template")
