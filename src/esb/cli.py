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
from zoneinfo import ZoneInfo

from esb import __version__
from esb import commands as esb_commands
from esb.config import ESBConfig
from esb.lib.langs import LangMap


###########################################################
# Parser Types
###########################################################
def aoc_year(value: str):
    now = datetime.now(tz=ZoneInfo("EST"))

    if value == "all":
        return list(range(ESBConfig.first_year, now.year + 1))

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
        return list(range(ESBConfig.first_day, ESBConfig.last_day + 1))

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


def aoc_part(value: str):
    if value == "all":
        return ESBConfig.parts

    try:
        ivalue = int(value)
        if ivalue not in ESBConfig.parts:
            message = f"{value} is not a valid AoC part. Please chose 1 or/and 2."
            raise argparse.ArgumentTypeError(message)

        return ivalue
    except ValueError as exc:
        message = f"{value} is not a valid AoC part"
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
    init = auto()
    fetch = auto()
    start = auto()
    show = auto()
    status = auto()
    test = auto()
    run = auto()
    dashboard = auto()


def set_arguments(parser, args, kwargs):
    parser.add_argument(*args, **kwargs)


def esb_parser() -> argparse.ArgumentParser:
    description = (
        "Script your way to rescue Christmas as part of the ElfScript Brigade team.\n\n"
        "`esb` is a CLI tool to help us _elves_ to save Christmas for the [Advent Of Code](https://adventofcode.com/)"
        " yearly events (Thank you [Eric 😉!](https://twitter.com/ericwastl)).\n"
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

    cmd_descriptions = {
        Command.init: "Initializes the ESB repo tool",
        Command.fetch: "Fetches problem statement and data",
        Command.start: "Prepares boilerplate code for the given language and day",
        Command.show: "Show problem statement and answers",
        Command.status: "Checks progress",
        Command.test: "Runs test cases",
        Command.run: "Runs with real input",
        Command.dashboard: "Rebuilds the dashboard",
    }

    parsers = {cmd: subparsers.add_parser(cmd.name, description=cmd_descriptions[cmd]) for cmd in Command}

    # Arguments
    force_arg = (
        ["-f", "--force"],
        {"action": "store_true", "help": "Ignore cache and fetch again"},
    )
    year_arg = (
        ["-y", "--year"],
        {"nargs": "+", "type": aoc_year, "help": "AoC year"},
    )
    day_arg = (
        ["-d", "--day"],
        {"nargs": "+", "type": aoc_day, "help": "AoC day"},
    )
    lang_arg = (
        ["-l", "--language"],
        {
            "action": AocLangAction,
            "lmap": lmap,
            "choices": lmap.names,
        },
    )
    submit_arg = (
        ["-s", "--submit"],
        {"action": "store_true", "help": "Submits solution"},
    )
    part_arg = (
        ["-p", "--part"],
        {
            "nargs": "+",
            "type": aoc_part,
            "help": "Runs part 1, part 2 or both parts",
        },
    )
    filter_arg = (
        ["-f", "--filter"],
        {
            "help": "Filters the tests with substring match",
        },
    )
    show_input_arg = (
        ["--show-input"],
        {"action": "store_true", "help": "Shows puzzle input"},
    )
    show_test_arg = (
        ["--show-test"],
        {"action": "store_true", "help": "Shows puzzle tests"},
    )
    reset_arg = (
        ["--reset"],
        {"action": "store_true", "help": "Resets the dashboard"},
    )
    full_arg = (
        ["-f", "--full"],
        {
            "action": "store_true",
            "help": "Shows full report with plots",
        },
    )

    # New
    # Fetch
    set_arguments(parsers[Command.fetch], *year_arg)
    set_arguments(parsers[Command.fetch], *day_arg)
    set_arguments(parsers[Command.fetch], *force_arg)

    # Start
    set_arguments(parsers[Command.start], *year_arg)
    set_arguments(parsers[Command.start], *day_arg)
    set_arguments(parsers[Command.start], *lang_arg)
    set_arguments(parsers[Command.start], *force_arg)

    # Show
    set_arguments(parsers[Command.show], *year_arg)
    set_arguments(parsers[Command.show], *day_arg)
    set_arguments(parsers[Command.show], *show_input_arg)
    set_arguments(parsers[Command.show], *show_test_arg)

    # Status
    set_arguments(parsers[Command.status], *full_arg)
    # Test
    set_arguments(parsers[Command.test], *year_arg)
    set_arguments(parsers[Command.test], *day_arg)
    set_arguments(parsers[Command.test], *lang_arg)
    set_arguments(parsers[Command.test], *part_arg)
    set_arguments(parsers[Command.test], *filter_arg)

    # Run
    set_arguments(parsers[Command.run], *year_arg)
    set_arguments(parsers[Command.run], *day_arg)
    set_arguments(parsers[Command.run], *lang_arg)
    set_arguments(parsers[Command.run], *part_arg)
    set_arguments(parsers[Command.run], *submit_arg)

    # Dashboard
    set_arguments(parsers[Command.dashboard], *reset_arg)

    return parser


def normalize_arg(args, name):
    if not hasattr(args, name):
        return args
    arg = getattr(args, name)
    if arg is None:
        arg = []
    setattr(args, name, list(set(arg)))
    return args


###########################################################
# CLI main
###########################################################
def main():
    parser = esb_parser()
    args = parser.parse_args()
    command = Command[args.command]

    args = normalize_arg(args, "year")
    args = normalize_arg(args, "day")
    args = normalize_arg(args, "part")

    match command:
        case Command.init:
            cmd = esb_commands.Init()
        case Command.fetch:
            cmd = esb_commands.Fetch(args.year, args.day, force=args.force)
        case Command.start:
            cmd = esb_commands.Start(args.language, args.year, args.day, force=args.force)
        case Command.show:
            cmd = esb_commands.Show(args.year, args.day, show_input=args.show_input, show_test=args.show_test)
        case Command.status:
            cmd = esb_commands.Status(full=args.full)
        case Command.run:
            cmd = esb_commands.Run(args.language, args.year, args.day, args.part, submit=args.submit)
        case Command.test:
            cmd = esb_commands.Test(args.language, args.year, args.day, args.part, args.filter)
        case Command.dashboard:
            cmd = esb_commands.Dashboard(reset=args.reset)
        case _:  # pragma: no cover
            message = "Should never reach here :thinking_face:"
            raise ValueError(message)
    cmd.execute()
    if cmd.esb_repo:
        cmd.update_arg_cache()
