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
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import patch

import pytest

from esb.protocol.fireplace import (
    FPPart,
    FPStatus,
    MetricPrefix,
    exec_protocol_from_file,
    parse_running_time,
    v1_run,
)

PT2_SOLUTION = 2
TEST_INPUT = "Any input"
TWO_LINES_INPUT = """Two lines
input"""


def solve_pt1(input_data: str, args: list[str] | None = None) -> str:
    if args is not None:
        return " ".join(args)
    return input_data.strip()


def solve_pt2(_input_data: str, _args: list[str] | None = None) -> int:
    return PT2_SOLUTION


class TestRunSolutions:
    command_args_pt1 = ("--part", "1")
    command_args_pt2 = ("--part", "2")

    @staticmethod
    def v1_run_context(input_data: str, command_args: tuple[str, ...]):
        input_io = io.StringIO(input_data)
        with (
            patch("sys.argv", ["command_name", *command_args]),
            patch("sys.stdin", input_io),
            patch("sys.stderr", new_callable=io.StringIO),
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            v1_run(solve_pt1, solve_pt2)
            return stdout.getvalue()

    def test_v1_run_should_fail_when_not_passing_correct_arguments(self):
        with pytest.raises(SystemExit, match="2"):
            self.v1_run_context(TEST_INPUT, ())

    def test_v1_run_should_print_the_solution_value_in_the_first_line(self):
        output = self.v1_run_context(TEST_INPUT, self.command_args_pt1)
        assert output.startswith(f"{TEST_INPUT}\n")

    def test_v1_run_should_print_the_running_time_in_the_second_line(self):
        output = self.v1_run_context(TEST_INPUT, self.command_args_pt1)
        time, unit = parse_running_time(output.removeprefix(f"{TEST_INPUT}\n"))
        assert isinstance(time, int)
        assert isinstance(unit, MetricPrefix)

    def test_v1_run_should_have_two_lines(self):
        output = self.v1_run_context(TEST_INPUT, self.command_args_pt1)
        assert len(output.removesuffix("\n").split("\n")) == 2

    def test_v1_run_should_may_have_more_than_two_lines(self):
        output = self.v1_run_context(TWO_LINES_INPUT, self.command_args_pt1)
        assert (
            len(output.removesuffix("\n").split("\n")) == 3  # Two from input + 1 from RT
        )

    def test_v1_run_must_run_the_solution_pt2(self):
        output = self.v1_run_context(TEST_INPUT, self.command_args_pt2)
        assert output.startswith(f"{PT2_SOLUTION}\n")

    def test_v1_run_must_accept_shorthand_part_argument(self):
        command = ("-p", "2")
        output = self.v1_run_context(TEST_INPUT, command)
        assert output.startswith(f"{PT2_SOLUTION}\n")

    def test_v1_run_must_accept_optional_positional_arguments(self):
        args = ("a", "b", "c")
        command = ("-p", "1", "--args", *args)
        output = self.v1_run_context(TEST_INPUT, command)
        assert output.startswith(f"{' '.join(args)}\n")


class TestExecProtocol:
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

    def test_exec_protocol_can_output_more_than_one_line(self):
        result = self.exec_protocol_from_file_context(self.command, part=1, cwd=Path.cwd(), input_data=TWO_LINES_INPUT)
        assert result.status == FPStatus.Ok
        assert result.answer == TWO_LINES_INPUT
        assert isinstance(result.running_time, int)
        assert isinstance(result.unit, MetricPrefix)


class TestMetricPrefix:
    sample_value = 1.23

    @pytest.mark.parametrize(
        ("unit", "value"),
        [
            ("Qm", MetricPrefix.quetta),
            ("Rm", MetricPrefix.ronna),
            ("Ym", MetricPrefix.yotta),
            ("Zm", MetricPrefix.zetta),
            ("Em", MetricPrefix.exa),
            ("Pm", MetricPrefix.peta),
            ("Tm", MetricPrefix.tera),
            ("Gm", MetricPrefix.giga),
            ("Mm", MetricPrefix.mega),
            ("km", MetricPrefix.kilo),
            ("m", MetricPrefix._),  # noqa: SLF001
            ("mm", MetricPrefix.milli),
            ("μm", MetricPrefix.micro),
            ("nm", MetricPrefix.nano),
            ("pm", MetricPrefix.pico),
            ("fm", MetricPrefix.femto),
            ("am", MetricPrefix.atto),
            ("zm", MetricPrefix.zepto),
            ("ym", MetricPrefix.yocto),
            ("rm", MetricPrefix.ronto),
            ("qm", MetricPrefix.quecto),
            ("quettameters", MetricPrefix.quetta),
            ("ronnameters", MetricPrefix.ronna),
            ("yottameters", MetricPrefix.yotta),
            ("zettameters", MetricPrefix.zetta),
            ("exameters", MetricPrefix.exa),
            ("petameters", MetricPrefix.peta),
            ("terameters", MetricPrefix.tera),
            ("gigameters", MetricPrefix.giga),
            ("megameters", MetricPrefix.mega),
            ("kilometers", MetricPrefix.kilo),
            ("meters", MetricPrefix._),  # noqa: SLF001
            ("millimeters", MetricPrefix.milli),
            ("micrometers", MetricPrefix.micro),
            ("nanometers", MetricPrefix.nano),
            ("picometers", MetricPrefix.pico),
            ("femtometers", MetricPrefix.femto),
            ("attometers", MetricPrefix.atto),
            ("zeptometers", MetricPrefix.zepto),
            ("yoctometers", MetricPrefix.yocto),
            ("rontometers", MetricPrefix.ronto),
            ("quectometers", MetricPrefix.quecto),
        ],
    )
    def test_parse_success(self, unit, value):
        assert MetricPrefix.parse(unit, "meter", "m") is value

    @pytest.mark.parametrize(
        "test_value",
        [
            "abc",
            "petermeters",
            "nanopeters",
            "Xm",
        ],
    )
    def test_parse_fail(self, test_value):
        with pytest.raises(ValueError, match="Cannot parse"):
            MetricPrefix.parse(test_value, "meter", "m")

    @pytest.mark.parametrize(
        ("test_value", "answer"),
        [
            (MetricPrefix._, 0),  # noqa: SLF001
            (MetricPrefix.nano, -9),
            (MetricPrefix.kilo, 3),
        ],
    )
    def test_serialize(self, test_value, answer):
        assert test_value.serialize() == answer

    @pytest.mark.parametrize(
        ("test_value", "answer"),
        [
            (0, MetricPrefix._),  # noqa: SLF001
            (-9, MetricPrefix.nano),
            (3, MetricPrefix.kilo),
        ],
    )
    def test_deserialize(self, test_value, answer):
        assert MetricPrefix.deserialize(test_value) is answer

    @pytest.mark.parametrize(
        ("test_value", "sample_value", "answer"),
        [
            (MetricPrefix._, sample_value, sample_value),  # noqa: SLF001
            (MetricPrefix.nano, sample_value, sample_value * 1e-9),
            (MetricPrefix.kilo, sample_value, sample_value * 1e3),
        ],
    )
    def test_to_float(self, test_value, sample_value, answer):
        assert test_value.to_float(sample_value) == pytest.approx(answer)

    @pytest.mark.parametrize(
        ("test_value", "answer_mantissa", "answer_exponent"),
        [
            (sample_value, sample_value, MetricPrefix._),  # noqa: SLF001
            (sample_value * 1e3, sample_value, MetricPrefix.kilo),
            (sample_value * 1e-9, sample_value, MetricPrefix.nano),
        ],
    )
    def test_from_float(self, test_value, answer_mantissa, answer_exponent):
        val, mprefix = MetricPrefix.from_float(test_value)
        assert pytest.approx(val) == answer_mantissa
        assert mprefix is answer_exponent

    def test_from_float_raises(self):
        with pytest.raises(ValueError, match="is not a valid MetricPrefix"):
            MetricPrefix.from_float(1e123)

    @pytest.mark.parametrize(
        ("test_value", "test_exponent", "answer_mantissa", "answer_exponent"),
        [
            (sample_value, 3, sample_value, MetricPrefix.kilo),
            (sample_value * 1e3, 3, sample_value, MetricPrefix.mega),
            (sample_value * 1e-9, 3, sample_value, MetricPrefix.micro),
        ],
    )
    def test_from_float_with_exponent(self, test_value, test_exponent, answer_mantissa, answer_exponent):
        val, mprefix = MetricPrefix.from_float(test_value, test_exponent)
        assert pytest.approx(val) == answer_mantissa
        assert mprefix is answer_exponent

    @pytest.mark.parametrize(
        ("test_value", "sample_value", "answer"),
        [
            (MetricPrefix._, sample_value, f"{sample_value} meters"),  # noqa: SLF001
            (MetricPrefix.nano, sample_value, f"{sample_value} nanometers"),
            (MetricPrefix.kilo, sample_value, f"{sample_value} kilometers"),
        ],
    )
    def test_format(self, test_value, sample_value, answer):
        assert test_value.format(sample_value, "meters") == answer
