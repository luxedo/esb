"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from __future__ import annotations

import io
import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import patch

import pytest

from esb.protocol.fireplacev1_0 import (
    FPPart,
    FPStatus,
    MetricPrefix,
    _parse_running_time,
    exec_protocol_from_file,
    run_solutions,
)

PT2_SOLUTION = 2
TEST_INPUT = "Any input"


def solve_pt1(input_data: str, args: list[str] | None = None) -> str:
    if args is not None:
        return " ".join(args)
    return input_data.strip()


def solve_pt2(_input_data: str, _args: list[str] | None = None) -> int:
    return PT2_SOLUTION


class TestRunSolutions(unittest.TestCase):
    command_args_pt1 = ("--part", "1")
    command_args_pt2 = ("--part", "2")

    @staticmethod
    def run_solutions_context(input_data: str, command_args: tuple[str, ...]):
        input_io = io.StringIO(input_data)
        with patch("sys.argv", ["command_name", *command_args]), patch("sys.stdin", input_io), patch(
            "sys.stderr", new_callable=io.StringIO
        ), patch("sys.stdout", new_callable=io.StringIO) as stdout:
            run_solutions(solve_pt1, solve_pt2)
            return stdout.getvalue()

    def test_run_solutions_should_fail_when_not_passing_correct_arguments(self):
        with pytest.raises(SystemExit, match="2"):
            self.run_solutions_context(TEST_INPUT, ())

    def test_run_solutions_should_print_the_solution_value_in_the_first_line(self):
        output = self.run_solutions_context(TEST_INPUT, self.command_args_pt1)
        assert output.startswith(f"{TEST_INPUT}\n")

    def test_run_solutions_should_print_the_running_time_in_the_second_line(self):
        output = self.run_solutions_context(TEST_INPUT, self.command_args_pt1)
        time, unit = _parse_running_time(output.removeprefix(f"{TEST_INPUT}\n"))
        assert isinstance(time, int)
        assert isinstance(unit, MetricPrefix)

    def test_run_solutions_should_have_only_two_lines(self):
        output = self.run_solutions_context(TEST_INPUT, self.command_args_pt1)
        assert len(output.removesuffix("\n").split("\n")) == 2

    def test_run_solutions_must_run_the_solution_pt2(self):
        output = self.run_solutions_context(TEST_INPUT, self.command_args_pt2)
        assert output.startswith(f"{PT2_SOLUTION}\n")

    def test_run_solutions_must_accept_shorthand_part_argument(self):
        command = ("-p", "2")
        output = self.run_solutions_context(TEST_INPUT, command)
        assert output.startswith(f"{PT2_SOLUTION}\n")

    def test_run_solutions_must_accept_optional_positional_arguments(self):
        args = ("a", "b", "c")
        command = ("-p", "1", "--args", *args)
        output = self.run_solutions_context(TEST_INPUT, command)
        assert output.startswith(f"{' '.join(args)}\n")


class TestExecProtocol(unittest.TestCase):
    command = ("python", "tests/mock/solution.py")

    @staticmethod
    def exec_protocol_from_file_context(command: tuple[str, ...], part: FPPart, cwd: Path, input_data: str):
        with NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as fp:
            fp.write(input_data)
            fp.seek(0)
            result = exec_protocol_from_file(list(command), part=part, args=None, cwd=cwd, day_input=Path(fp.name))
            fp.close()
        return result

    def test_exec_protocol_from_file_runs_successfully_part_1(self):
        result = self.exec_protocol_from_file_context(self.command, part=1, cwd=Path.cwd(), input_data=TEST_INPUT)
        assert result.status == FPStatus.Ok
        assert result.answer == TEST_INPUT
        assert isinstance(result.running_time, int)
        assert isinstance(result.unit, MetricPrefix)

    def test_exec_protocol_from_file_runs_successfully_part_2(self):
        result = self.exec_protocol_from_file_context(self.command, part=2, cwd=Path.cwd(), input_data=TEST_INPUT)
        assert result.status == FPStatus.Ok
        assert result.answer == str(PT2_SOLUTION)
        assert isinstance(result.running_time, int)
        assert isinstance(result.unit, MetricPrefix)

    def test_exec_protocol_from_file_fails_when_no_input_is_found(self):
        result = exec_protocol_from_file(
            list(self.command),
            part=1,
            args=None,
            cwd=Path.cwd(),
            day_input=Path("This input does not exists"),
        )
        assert result.status == FPStatus.InputDoesNotExists
