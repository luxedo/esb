# ESB - ElfScript Brigade

> Script your way to rescue Christmas as part of the ElfScript Brigade team.

<img src="doc/logo/png/logo-color-small.png" alt="ElfScript Brigade Logo"/>

[![PyPI - Version](https://img.shields.io/pypi/v/esb.svg)](https://pypi.org/project/esb)[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/esb.svg)](https://pypi.org/project/esb)[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)

---

In the bureaucratic workshop of Santa's IT department, where the spirit of Christmas and the magic of coding converge, a special group of coding elves emerged known as the **ElfScript Brigade**. These skilled and whimsical elves were bestowed with the mission of safeguarding the joyous essence of Christmas through the power of scripting and coding.



`esb` is a CLI tool to help us _elves_ to save Christmas for the [Advent Of Code](https://adventofcode.com/) yearly events (Thank you [Eric 😉!](https://twitter.com/ericwastl)).

This tool allows us _elves_ to:

1. Fetch puzzle statement and puzzle data
2. Create code boilerplate<sup>\*[Check supported languages](##...)</sup>
3. Test run and submit solutions
4. [Shiny dashboards](...)

## Table of Contents

- [Installation](##installation)
- [Usage](##usage)
- [Currently supported languages](##...)
- [License](##license)

## Installation

```console
pip install esb
```

## Usage

### Initializing the repository

Create a `git` repository and initialize an `esb` repository too.

```console
mkdir my_aoc_repo
cd my_aoc_repo
git init
esb init
git commit -m  "I now pledge to help, and I will forever help, saving christmas."
```

### Add your credentials

Set your credentials by locating your session cookie or save it in a `.env` file. If the cookie expires, you'll have to redo this step for fetching and submitting data.

@TODO: Show how to get the cookie

```console
export AOC_SESSION_COOKIE="<my_current_cookie>"
# Or
echo "<my_current_cookie>" > .env
```

### Fetching problems

Downloads puzzle statement, data and correct answers (when applicable).

```console
export AOC_SESSION_COOKIE="<my_current_cookie>"
esb fetch --year 2016 --day 9
```

### Running tests

Runs tests or selected tests

```console
# Run all
esb test --all

# Run all from specific language
esb test --year 2016 --day 9 --lang rust --all

# Run single test
esb test --year 2016 --day 9 --lang rust --all
```

### Running for real

Runs the code for the given input. Also can submit solutions.

```console
esb run --year 2016 --day 9 --lang rust

esb run --year 2016 --day 9 --lang rust --submit
```

### The dashboards

The dashboards are created automatically when events happen. It's possible to generate
again by running:

```console
esb dashboard
```

## Currently supported languages

Currently there are built in 3 supported languages. They set up the basic code for a
given day that allows `esb` to run and test solutions. Check the documentation
for each language and how to create your own boilerplate.

- Python
- Rust
- Elixir
- _Create your own_

## License

> ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.
> Copyright (C) 2024 Luiz Eduardo Amaral <luizamaral306@gmail.com>
>
> This program is free software: you can redistribute it and/or modify
> it under the terms of the GNU General Public License as published by
> the Free Software Foundation, either version 3 of the License, or
> (at your option) any later version.
> This program is distributed in the hope that it will be useful,
> but WITHOUT ANY WARRANTY; without even the implied warranty of
> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
> GNU General Public License for more details.
> You should have received a copy of the GNU General Public License
> along with this program.  If not, see <http://www.gnu.org/licenses/>.
