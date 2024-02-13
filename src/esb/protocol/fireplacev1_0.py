"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Literal

if TYPE_CHECKING:
    from pathlib import Path

AocSolutionFn = Callable[[str], Any]


###########################################################
# Python template runner
###########################################################
def _run_solution(part: Literal[1, 2], solve_pt1: AocSolutionFn, solve_pt2: AocSolutionFn):
    match part:
        case 1:
            return solve_pt1(sys.stdin.read())
        case 2:
            return solve_pt2(sys.stdin.read())
        case _:
            message = f"Part {part} does not exist"
            raise KeyError(message)


def run_solutions(solve_pt1: AocSolutionFn, solve_pt2: AocSolutionFn):
    parser = argparse.ArgumentParser("")
    parser.add_argument(
        "-p",
        "--part",
        choices=[1, 2],
        required=True,
        type=int,
        help="Run solution part 1 or part 2",
    )
    parser.add_argument(
        "-a",
        "--args",
        nargs="*",
        help="Run solution part 1 or part 2",
    )
    args = parser.parse_args()
    ans = _run_solution(args.part, solve_pt1, solve_pt2)
    sys.stdout.write(f"{ans}")


###########################################################
# Protocol runner
###########################################################
class MetricPrefix(Enum):
    quetta = 30
    Q = 30  # noqa: PIE796
    ronna = 27
    R = 27  # noqa: PIE796
    yotta = 24
    Y = 24  # noqa: PIE796
    zetta = 21
    Z = 21  # noqa: PIE796
    exa = 18
    E = 18  # noqa: PIE796
    peta = 15
    P = 15  # noqa: PIE796
    tera = 12
    T = 12  # noqa: PIE796
    giga = 9
    G = 9  # noqa: PIE796
    mega = 6
    M = 6  # noqa: PIE796
    kilo = 3
    k = 3  # noqa: PIE796
    hecto = 2
    h = 2  # noqa: PIE796
    deca = 1
    da = 1  # noqa: PIE796
    _ = 0
    deci = -1
    d = -1  # noqa: PIE796
    centi = -2
    c = -2  # noqa: PIE796
    milli = -3
    m = -3  # noqa: PIE796
    micro = -6
    μ = -6  # noqa: PIE796 PLC2401
    nano = -9
    n = -9  # noqa: PIE796
    pico = -12
    p = -12  # noqa: PIE796
    femto = -15
    f = -15  # noqa: PIE796
    atto = -18
    a = -18  # noqa: PIE796
    zepto = -21
    z = -21  # noqa: PIE796
    yocto = -24
    y = -24  # noqa: PIE796
    ronto = -27
    r = -27  # noqa: PIE796
    quecto = -30
    q = -30  # noqa: PIE796


class FPStatus(Enum):
    Ok = auto()
    InputDoesNotExists = auto()
    ProtocolError = auto()


@dataclass(frozen=True)
class FPResult:
    status: FPStatus
    stdout: str = ""
    stderr: str = ""
    time: int | None = None
    time_unit: MetricPrefix | None = None


FPPart = Literal[1, 2]


# @TODO: type this
async def _read_output(stream, threshold, print_stream):
    ret = ""
    lines = 0
    while line := await stream.readline():
        line = line.decode("utf-8")
        ret += line
        if lines == threshold:
            print_stream.write(ret)
        elif lines > threshold:
            print_stream.write(line)
        lines += 1
    return ret, lines


async def _exec_protocol_command(
    cmd: list[str], cwd: Path, day_input: Path
) -> tuple[int, tuple[str, int], tuple[str, int]]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=cwd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    if proc.stdin is None:
        message = "Could not open stdin"
        raise RuntimeError(message)

    proc.stdin.write(day_input.read_text().encode())
    proc.stdin.close()

    # Wait for the process to complete and tasks to finish
    return await asyncio.gather(
        proc.wait(),
        _read_output(proc.stdout, threshold=1, print_stream=sys.stdout),
        _read_output(proc.stderr, threshold=0, print_stream=sys.stderr),
    )


def exec_protocol(command: list[str], part: FPPart, cwd: Path, day_input: Path) -> FPResult:
    if not day_input.is_file():
        return FPResult(status=FPStatus.InputDoesNotExists)

    cmd = [*command, "--part", f"{part}"]
    exitcode, (stdout, out_lines), (stderr, err_lines) = asyncio.run(_exec_protocol_command(cmd, cwd, day_input))
    status = FPStatus.Ok
    success_exit = 0
    stdout_max_lines = 1
    stderr_max_lines = 2
    if exitcode != success_exit or out_lines > stdout_max_lines or err_lines > stderr_max_lines:
        status = FPStatus.ProtocolError

    return FPResult(status, stdout, stderr)
