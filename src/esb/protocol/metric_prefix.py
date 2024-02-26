"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from __future__ import annotations

from enum import Enum


class MetricPrefixAbbrev(Enum):
    Q = 30
    R = 27
    Y = 24
    Z = 21
    E = 18
    P = 15
    T = 12
    G = 9
    M = 6
    k = 3
    h = 2
    _ = 0
    d = -1
    c = -2
    m = -3
    μ = -6  # noqa: PLC2401
    n = -9
    p = -12
    f = -15
    a = -18
    z = -21
    y = -24
    r = -27
    q = -30


class MetricPrefix(Enum):
    quetta = 30
    ronna = 27
    yotta = 24
    zetta = 21
    exa = 18
    peta = 15
    tera = 12
    giga = 9
    mega = 6
    kilo = 3
    hecto = 2
    deca = 1
    _ = 0
    deci = -1
    centi = -2
    milli = -3
    micro = -6
    nano = -9
    pico = -12
    femto = -15
    atto = -18
    zepto = -21
    yocto = -24
    ronto = -27
    quecto = -30

    @classmethod
    def parse(cls, value: str, suffix: str, abbrev: str) -> MetricPrefix:
        if value.endswith((suffix, suffix + "s")):
            match value.removesuffix("s").removesuffix(suffix):
                case "":
                    return cls._
                case unit:
                    return cls[unit]
        match value.removesuffix(abbrev):
            case "":
                return cls._
            case unit:
                mp_map = {member.value: member for member in MetricPrefix}
                return mp_map[MetricPrefixAbbrev[unit].value]

    def serialize(self):
        return self.value

    @classmethod
    def deserialize(cls, value):
        return cls(value)
