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
from enum import Enum, auto
from typing import get_args
from zoneinfo import ZoneInfo

from esb import __version__
from esb import commands as esb_commands
from esb.config import ESBConfig
from esb.langs import LangMap
from esb.protocol.fireplacev1_0 import FPPart


###########################################################
# Parser Types
###########################################################
def aoc_year(value: str):
    now = datetime.now(tz=ZoneInfo("EST"))

    if value == "all":
        return range(ESBConfig.first_year, now.year)

    try:
        ivalue = int(value)
        if ivalue < ESBConfig.first_year:
            message = f"{value} is not a valid AoC year. Please try from 2015 onwards."
            raise argparse.ArgumentTypeError(message)

        if ivalue > now.year:
            message = f"{value} is not a valid AoC year. Please try from 2015 up to {now.year - 1}."
            raise argparse.ArgumentTypeError(message)

        return ivalue
    except ValueError as exc:
        message = f"{value} is not a valid AoC year"
        raise argparse.ArgumentTypeError(message) from exc


def aoc_day(value: str):
    if value == "all":
        return range(ESBConfig.first_day, ESBConfig.last_day + 1)

    try:
        ivalue = int(value)
        if ivalue < ESBConfig.first_day:
            message = f"{value} is not a valid AoC day. Please try from 1 onwards."
            raise argparse.ArgumentTypeError(message)

        if ivalue > ESBConfig.last_day:
            message = f"{value} is not a valid AoC day. Please try from 1 up to 25."
            raise argparse.ArgumentTypeError(message)

        return ivalue
    except ValueError as exc:
        message = f"{value} is not a valid AoC day"
        raise argparse.ArgumentTypeError(message) from exc


class AocLangAction(argparse.Action):
    def __init__(self, lmap: LangMap, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lmap = lmap

    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest, self.lmap.get(value))


###########################################################
# Parser
###########################################################
class Command(Enum):
    new = auto()
    fetch = auto()
    start = auto()
    show = auto()
    status = auto()
    test = auto()
    run = auto()
    dashboard = auto()


def esb_parser() -> argparse.ArgumentParser:
    cmd_descriptions = {
        Command.new: "Initializes the ESB repo tool",
        Command.fetch: "Fetches problem statement and data",
        Command.start: "Prepares boilerplate code for the given language and day",
        Command.show: "Show problem statement and answers",
        Command.status: "Checks progress",
        Command.test: "Runs test cases",
        Command.run: "Runs with real input",
        Command.dashboard: "Rebuilds the dashboard",
    }

    description = (
        "Script your way to rescue Christmas as part of the ElfScript Brigade team.\n\n"
        "`esb` is a CLI tool to help us _elves_ to save Christmas for the [Advent Of Code](https://adventofcode.com/)"
        "yearly events (Thank you [Eric 😉!](https://twitter.com/ericwastl)).\n"
        "For more information visit https://github.com/luxedo/esb"
    )
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(
        title="command",
        description="What do you want to do?",
        required=True,
        dest="command",
    )
    lmap = LangMap.load()
    parsers = {}
    for cmd in Command:
        parsers[cmd] = subparsers.add_parser(cmd.name, description=cmd_descriptions[cmd])
        if cmd in {Command.fetch, Command.start}:
            parsers[cmd].add_argument(
                "-f",
                "--force",
                action="store_true",
                help="Ignore cache and fetch again",
            )

        if cmd in {Command.fetch, Command.start, Command.show}:
            parsers[cmd].add_argument("-y", "--year", required=True, nargs="+", type=aoc_year, help="AoC year")
            parsers[cmd].add_argument("-d", "--day", required=True, nargs="+", type=aoc_day, help="AoC day")

        if cmd == Command.start:
            parsers[cmd].add_argument(
                "-l",
                "--language",
                required=True,
                action=AocLangAction,
                lmap=lmap,
                choices=lmap.names,
            )

        if cmd in {Command.test, Command.run}:
            parsers[cmd].add_argument(
                "-l",
                "--language",
                required=True,
                action=AocLangAction,
                lmap=lmap,
                choices=lmap.names,
            )
            parsers[cmd].add_argument("-y", "--year", nargs="+", type=aoc_year, help="AoC year")
            parsers[cmd].add_argument("-d", "--day", nargs="+", type=aoc_day, help="AoC day")

        if cmd in {Command.run, Command.test}:
            parsers[cmd].add_argument("-s", "--submit", action="store_true", help="Submits solution")
            parsers[cmd].add_argument(
                "-p",
                "--parts",
                required=True,
                choices=get_args(FPPart),
                type=int,
                help="Run for part 1 or part 2",
            )

    return parser


###########################################################
# CLI main
###########################################################
def main():
    parser = esb_parser()
    args = parser.parse_args()
    command = Command[args.command]

    match command:
        case Command.new:
            esb_commands.new()
        case Command.fetch:
            esb_commands.fetch(args.year, args.day, force=args.force)
        case Command.start:
            esb_commands.start(args.language, args.year, args.day, force=args.force)
        case Command.show:
            esb_commands.show(args.year, args.day)
        case Command.status:
            esb_commands.status()
        case Command.run:
            esb_commands.run(args.language, args.parts, args.year, args.day, submit=args.submit)
        case Command.test:
            esb_commands.test(args.language, args.parts, args.year, args.day)
        case _:
            message = "Should never reach here :thinking_face:"
            raise ValueError(message)
    #     case Command.run | Command.test:
    #         aoc_main(spec, RunMode[args.command], args.year, args.day)
    #     case Command.fetch:
    #         prepare_template(spec, args.year, args.day, cookie)
    #     case Command.fetch2:
    #         update_main_template(spec, args.year, args.day, cookie)
    #     case _:
    #         raise ValueError(f"Command '{args.command}' not found.")
