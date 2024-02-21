"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ESBConfig:
    # Paths
    db_path = Path("database/ElvenCrisisArchive.sqlite")
    package_root = Path(__file__).parent
    blank_dir = "blank"
    solutions_dir = "solutions"
    boiler_dir = "boilers"
    cache_dir = ".cache"
    boiler_template = "template"
    blank_root = package_root.parent / blank_dir
    solutions_root = package_root.parent / solutions_dir
    boiler_root = package_root.parent / boiler_dir
    spec_filename = "spec.json"
