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
    db_path = Path(".cache/ElvenCrisisArchive.sqlite")
    package_root = Path(__file__).parent
    blank_dir = "blank"
    solutions_dir = "solutions"
    boiler_dir = "boilers"
    cache_dir = ".cache"
    tests_dir = "tests"
    boiler_template = "template"
    boiler_template_base = "base"
    blank_root = package_root / blank_dir
    boiler_root = package_root / boiler_dir
    spec_filename = "spec.json"

    # AoC
    first_year = 2015
    first_day = 1
    last_day = 25
    all_days = tuple(range(first_day, last_day + 1))
    parts = (1, 2)
    part_1 = 1
    part_2 = 2
    max_parts = max(parts)

    # Report
    blank_dash = package_root / blank_dir / "README.md"
    blank_report = package_root / blank_dir / "REPORT.md"
    truncate_answer = 512
