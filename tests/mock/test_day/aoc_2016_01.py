"""
ElfScript Brigade

Advent Of Code 2016 Day 01
Python Solution

Day 1: No Time for a Taxicab

https://adventofcode.com/2016/day/1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Orientation(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


class Side(Enum):
    LEFT = -1
    RIGHT = 1

    @classmethod
    def from_str(cls, s: str) -> Side:
        if s == "L":
            return cls.LEFT
        if s == "R":
            return cls.RIGHT
        message = "Could not determine side"
        raise ValueError(message)


@dataclass(frozen=True, eq=True)
class Coord:
    x: int = 0
    y: int = 0


@dataclass
class Taxi:
    orientation: Orientation = Orientation.NORTH
    position: Coord = field(default_factory=Coord)

    def turn(self, side: Side):
        self.orientation = Orientation((self.orientation.value + side.value) % len(Orientation))

    def step(self, steps: int):
        x, y = self.position.x, self.position.y
        match self.orientation:
            case Orientation.NORTH:
                y += steps
            case Orientation.EAST:
                x += steps
            case Orientation.SOUTH:
                y -= steps
            case Orientation.WEST:
                x -= steps
        self.position = Coord(x, y)

    def manhattan(self) -> int:
        return abs(self.position.x) + abs(self.position.y)


def parse_input(input_data: str) -> list[tuple[Side, int]]:
    return [(Side.from_str(d[0]), int(d[1:])) for d in input_data.strip().split(", ")]


def solve_pt1(input_data: str, _args: list[str] | None = None) -> int:
    taxi = Taxi()
    for side, steps in parse_input(input_data):
        taxi.turn(side)
        taxi.step(steps)
    return taxi.manhattan()


def solve_pt2(input_data: str, _args: list[str] | None = None) -> int:
    taxi = Taxi()
    seen = {taxi.position}
    for side, steps in parse_input(input_data):
        taxi.turn(side)
        for _ in range(steps):
            taxi.step(1)
            if taxi.position in seen:
                return taxi.manhattan()
            seen.add(taxi.position)
    return taxi.manhattan()


if __name__ == "__main__":
    from esb.protocol import fireplace

    # 🎅🎄❄️☃️🎁🦌
    # Bright christmas lights HERE
    fireplace.v1_run(solve_pt1, solve_pt2)
