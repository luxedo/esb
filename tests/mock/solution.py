"""
ElfScript Brigade

Python Mock Solution
"""

from __future__ import annotations

PT2_SOLUTION = 2
TEST_INPUT = "Any input"


def solve_pt1(input_data: str, args: list[str] | None = None) -> str:
    if args is not None:
        return " ".join(args)
    return input_data.strip()


def solve_pt2(_input_data: str, _args: list[str] | None = None) -> int:
    return PT2_SOLUTION


if __name__ == "__main__":
    from esb.protocol import fireplace

    # 🎅🎄❄️☃️🎁🦌
    # Bright christmas lights HERE
    fireplace.v1_run(solve_pt1, solve_pt2)
