# FIREPLACE v1.0
> Festive Intervention and Response Protocol for Elf Coding Emergencies v1.0

## Introduction
At the heart of the ElfScript Brigade's operational endeavors resides the _Fireplace Protocol Version 1.0_ (FIREPLACEv1.0), an enchanting and robust communication system. This protocol serves as the magical conduit through which coding elves engage in the exchange of solutions and collaborative efforts to overcome challenges that could potentially dampen the Christmas spirit.

The FIREPLACEv1.0 allows the use of the `esb` tooling for solving Advent of Code problems.

## Protocol Definition
### Premises
* This protocol is tailored to assist coding elves in solving [Advent of Code](https://adventofcode.com/) problems.
* Each problem consists of _PROBLEM DATA_, usually stored in a file, and an _ANSWER_ that should effectively solve the problem.
* The _RUNNING TIME_ of a _PROGRAM_  is the time the program took to execute, starting before parsing `stdin` data and ending just before returning the answer in `stdout`.

### Requirements
Any _PROGRAM_ implementing FIREPLACEv1.0 should receive the _PROBLEM DATA_ as input and return the _ANSWER_ as an output. The following requirements must be adhered to:

1. The _PROGRAM_ **MUST** receive _PROBLEM DATA_ via `stdin`.
1. The _PROGRAM_ **MUST** accept two arguments:
    1. `--part` or `-p`, a required argument with values of either `1` or `2`.
    1. `--args` or `-a`, optional positional arguments<sup>*</sup>.
1. The _PROGRAM_ **MUST** return the _ANSWER_ followed by a line break via `stdout`.
1. The _PROGRAM_ **MUST** return an exit code of `0` on successful execution. Any other code is considered an error.
1. The _PROGRAM_ **MAY** log a _RUNNING TIME_ followed by a line break via `stdout` after the _ANSWER_.
1. The _RUNNING TIME_ **MUST** be represented the following three elements sepearated by an spaces and ending with a line break:
    1. It's prefix of `RT`.
    1. it's _NUMERIC VALUE_.
    1. It's _UNIT_ in [metric prefix](https://en.wikipedia.org/wiki/Metric_prefix) followed by `seconds`, OR it's abbreviated symbol followed by `s`. Here's a micro `μ` symbol; you're welcome.
    1. Example: `RT 123 ns`
1. The _PROGRAM_ **MUST NOT** print other data besides the _ANSER_ and the _RUNNING TIME_
1. The _PROGRAM_ **MAY** output data in `stderr`. Any data in this stream will be ignored.
1. The _PROGRAM_ **MAY** implement an optional flag `--help` or `-h` that shows command usage.

<sup>*</sup> Some Advent of Code problems have different parameters for tests and for the _PROBLEM DATA_. As in [year 2023 day 21](https://adventofcode.com/2023/day/21), If that's the case, positional arguments are passed through the `--arg`.

## Examples:

Running programs

```shell
cat problem_data.txt | ./my_program --part 1
1234
```

```shell
./my_program --part 1 < problem_data.txt
1234
```

Running programs with running time
```shell
./my_program --part 1 --args a b c < problem_data.txt
SRTM 12 ms
1234
ERTM 7632 milliseconds
```
```shell
cat problem_data.txt | ./my_program --part 2
SRTM 24 ms
1234
ERTM 6833 milliseconds
```
