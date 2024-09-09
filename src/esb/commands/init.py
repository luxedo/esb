"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from __future__ import annotations

import sys
from pathlib import Path

from esb.commands.base import Command, eprint_error, eprint_info
from esb.lib.db import ElvenCrisisArchive
from esb.lib.paths import BlankSled


class Init(Command):
    esb_repo: bool = False

    @staticmethod
    def execute():
        eprint_info("Initializing a new ElfScript Brigade repository")
        cwd = Path.cwd()

        bs = BlankSled(Path.cwd())

        if len(bs.repo_conflicts()) > 0:
            eprint_error(
                "Directory not clean! Cannot initialize. Please start the repo in a (somewhat) clean directory"
            )
            sys.exit(1)

        try:
            bs.new_repo()
        except OSError:
            eprint_error("Something went wrong! Could not initialize esb repo")
            sys.exit(1)

        ElvenCrisisArchive(cwd).new_repo()

        eprint_info("ESB repo is ready! Thank you for saving Christmas [italic]Elf[/italic]")
