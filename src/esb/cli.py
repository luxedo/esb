"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).


Copyright (C) 2024 Luiz Eduardo Amaral <luizamaral306@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import argparse
from datetime import datetime
from enum import Enum


def _aoc_year(value: str):
    # @TODO: Implement logic to get up to the current day

    now = datetime.now()

    if value == "all":
        return range(2015, now.year)

    try:
        ivalue = int(value)
        if ivalue < 2015:
            raise argparse.ArgumentTypeError(
                f"{value} is not a valid AoC year. Please try from 2015 onwards."
            )

        if ivalue > now.year:
            raise argparse.ArgumentTypeError(
                f"{value} is not a valid AoC year. Please try from 2015 up to {now.year-1}."
            )

        return [ivalue]
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} is not a valid AoC year")


def _aoc_day(value):
    if value == "all":
        return range(1, 26)

    try:
        ivalue = int(value)
        if ivalue < 1:
            raise argparse.ArgumentTypeError(
                f"{value} is not a valid AoC day. Please try from 1 onwards."
            )

        if ivalue > 25:
            raise argparse.ArgumentTypeError(
                f"{value} is not a valid AoC day. Please try from 1 up to 25."
            )

        return [ivalue]
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} is not a valid AoC day")


def esb_parser() -> argparse.ArgumentParser:
    class Command(Enum):
        init = 0
        fetch = 1
        test = 2
        run = 3
        dashboard = 4

    class Languages(Enum):
        python = 0

    cmd_descriptions = {
        Command.init: "Initializes the ESB repo tool",
        Command.fetch: "Fetches problem statement and data",
        Command.test: "Runs test cases",
        Command.run: "Runs with real input",
        Command.dashboard: "Rebuilds the dashboard",
    }

    parser = argparse.ArgumentParser(
        description="Script your way to rescue Christmas as part of the ElfScript Brigade team."
    )

    subparsers = parser.add_subparsers(
        title="command",
        description="What do you want to do?",
        required=True,
    )
    parsers = {}
    for cmd in Command:
        parsers[cmd] = subparsers.add_parser(
            cmd.name, description=cmd_descriptions[cmd]
        )

        if cmd == Command.fetch:
            parsers[cmd].add_argument(
                "-y", "--year", required=True, type=_aoc_year, help="AoC year"
            )
            parsers[cmd].add_argument(
                "-d", "--day", required=True, type=_aoc_day, help="AoC day"
            )

        if cmd in [Command.test, Command.run]:
            parsers[cmd].add_argument(
                "-l", "--lang", choices=[lang.name for lang in Languages]
            )
            parsers[cmd].add_argument("-y", "--year", type=_aoc_year, help="AoC year")
            parsers[cmd].add_argument("-d", "--day", type=_aoc_day, help="AoC day")
            parsers[cmd].add_argument(
                "-a", "--all", action="store_true", help="Runs all selected"
            )

        if cmd == Command.run:
            parsers[cmd].add_argument(
                "-s", "--submit", action="store_true", help="Submits solution"
            )

    return parser


def main():
    parser = esb_parser()
    _args = parser.parse_args()

    # cookie = environ.get("AOC_SESSION_COOKIE")

    # spec = lang_specs[args.lang]
    # command = Command[args.command]
    # match command:
    #     case Command.run | Command.test:
    #         aoc_main(spec, RunMode[args.command], args.year, args.day)
    #     case Command.fetch:
    #         prepare_template(spec, args.year, args.day, cookie)
    #     case Command.fetch2:
    #         update_main_template(spec, args.year, args.day, cookie)
    #     case _:
    #         raise ValueError(f"Command '{args.command}' not found.")


# main()
