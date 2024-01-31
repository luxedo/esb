"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

import argparse
from datetime import datetime
from enum import Enum
from zoneinfo import ZoneInfo

from esb.commands import new


class Command(Enum):
    new = 0
    fetch = 1
    test = 2
    run = 3
    dashboard = 4


class Languages(Enum):
    python = 0


def _aoc_year(value: str):
    # @TODO: Implement logic to get up to the current day
    aoc_first_year = 2015

    now = datetime.now(tz=ZoneInfo("EST"))

    if value == "all":
        return range(aoc_first_year, now.year)

    try:
        ivalue = int(value)
        if ivalue < aoc_first_year:
            message = f"{value} is not a valid AoC year. Please try from 2015 onwards."
            raise argparse.ArgumentTypeError(message)

        if ivalue > now.year:
            message = f"{value} is not a valid AoC year. Please try from 2015 up to {now.year - 1}."
            raise argparse.ArgumentTypeError(message)

        return [ivalue]
    except ValueError as exc:
        message = f"{value} is not a valid AoC year"
        raise argparse.ArgumentTypeError(message) from exc


def _aoc_day(value):
    day_01 = 1
    day_25 = 25
    if value == "all":
        return range(day_01, day_25 + 1)

    try:
        ivalue = int(value)
        if ivalue < day_01:
            message = f"{value} is not a valid AoC day. Please try from 1 onwards."
            raise argparse.ArgumentTypeError(message)

        if ivalue > day_25:
            message = f"{value} is not a valid AoC day. Please try from 1 up to 25."
            raise argparse.ArgumentTypeError(message)

        return [ivalue]
    except ValueError as exc:
        message = f"{value} is not a valid AoC day"
        raise argparse.ArgumentTypeError(message) from exc


def esb_parser() -> argparse.ArgumentParser:
    cmd_descriptions = {
        Command.new: "Initializes the ESB repo tool",
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
        dest="command",
    )
    parsers = {}
    for cmd in Command:
        parsers[cmd] = subparsers.add_parser(cmd.name, description=cmd_descriptions[cmd])

        if cmd == Command.fetch:
            parsers[cmd].add_argument("-y", "--year", required=True, type=_aoc_year, help="AoC year")
            parsers[cmd].add_argument("-d", "--day", required=True, type=_aoc_day, help="AoC day")

        if cmd in {Command.test, Command.run}:
            parsers[cmd].add_argument("-l", "--lang", choices=[lang.name for lang in Languages])
            parsers[cmd].add_argument("-y", "--year", type=_aoc_year, help="AoC year")
            parsers[cmd].add_argument("-d", "--day", type=_aoc_day, help="AoC day")
            parsers[cmd].add_argument("-a", "--all", action="store_true", help="Runs all selected")

        if cmd == Command.run:
            parsers[cmd].add_argument("-s", "--submit", action="store_true", help="Submits solution")

    return parser


def main():
    parser = esb_parser()
    args = parser.parse_args()
    command = Command[args.command]

    match command:
        case Command.new:
            new()
    #     case Command.run | Command.test:
    #         aoc_main(spec, RunMode[args.command], args.year, args.day)
    #     case Command.fetch:
    #         prepare_template(spec, args.year, args.day, cookie)
    #     case Command.fetch2:
    #         update_main_template(spec, args.year, args.day, cookie)
    #     case _:
    #         raise ValueError(f"Command '{args.command}' not found.")
