"""
ElfScript Brigade

Advent Of Code {year} Day {day}
Python Solution

{problem_title}

https://{problem_url}
"""

from typing import Any


def solve_pt1(input_data: str, *args: list[Any]) -> int:
    ...


def solve_pt2(input_data: str, *args: list[Any]) -> int:
    ...


if __name__ == "__main__":
    from esb.protocol import fireplacev1_0 as fp1_0

    fp1_0.run_solutions(solve_pt1, solve_pt2)
