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

from esb.commands.base import is_esb_repo, oprint_error, oprint_info, oprint_warn
from esb.dash import CliDash
from esb.db import ElvenCrisisArchive
from esb.langs import LangMap

if TYPE_CHECKING:
    from pathlib import Path


@is_esb_repo
def status(repo_root: Path):
    db = ElvenCrisisArchive(repo_root)
    lmap = LangMap.load()
    cli_dash = CliDash(db, lmap)

    brigadista = cli_dash.brigadista()

    oprint_error("ELFSCRIPT BRIGADE STATUS REPORT\n")
    oprint_info(brigadista)
    oprint_warn("\nSERVICE STARS")

    ys = cli_dash.years_summary()

    for year in sorted(ys.keys(), reverse=True):
        summary = ys[year]
        oprint_info(f"\n{year}")
        oprint_warn(f"\n{summary}")
