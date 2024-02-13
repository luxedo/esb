# FIREPLACE v1.0
> Festive Intervention and Response Protocol for Elf Coding Expertise v1.0

## Introduction
At the heart of the ElfScript Brigade's operations lies the _Fireplace Protocol Version 1.0_ (FIREPLACEv1.0), a whimsical yet powerful communication system. This protocol serves as the enchanted conduit through which the coding elves exchange solutions and tackle challenges that may threaten the festive spirit.

## Abstract
The FIREPLACEv1.0 allows the use of the `esb` tool for any PROGRAM that follows this protocol.

## Program requirements
Any PROGRAM That folllows FIREPLACEv1.0:

1. MUST Receive problem inputs via `stdin`.
1. MUST Accept two arguments:
    1. `--part` or `-p` required argument with values of either `1` or `2`.
    1. `--args` or `-a` optional positional arguments @TODO: Why need args?
1. MUST Return the answer via `stdout`.
1. MUST Return an exit code of `0` on successful execution. Any other code is considered an error.
1. MAY log a _running time_ via `stderr`.
    1. _running time_ IS the time the program took to execute, starting before parsing `stdin` data and ending before returning the answer in `stdout`
    1. A _running time_ is represented by two _running time markers_ printed in `stdout`. One for _start time_, and other for _end time_.
    1. A _running time marker_ MUST be represented by it's _numeric value_ followed by a space and then a _unit_ eg: `12 ms`.
    1. A _running time marker_ _unit_ should be a [metric prefix](https://en.wikipedia.org/wiki/Metric_prefix) followed by `seconds`. It may be abbreviated to it's symbol followed by `s`. Here's a micro `μ` symbol, you're welcome.
    1. Each _running time marker_ MUST be shown in a single line without any other characters
    1.  _running time marker_ __start time_ MUST be identified with the string `SRTM=` just before the time and the unit
    1.  _running time marker_ __end time_ MUST be identified with the string `ERTM=` just before the time and the unit


Examples:
```shell
cat problem_data.txt | ./my_program --part 1
1234
```
```shell
./my_program --part 1 < problem_data.txt
1234
```

```shell
./my_program --part 1 --args < problem_data.txt
SRTM=12 ms
1234
ERTM=7632 milliseconds
```
