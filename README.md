# ESB - ElfScript Brigade

> ⚠️ This project is under development! It hasn't been released yet

> Script your way to rescue Christmas as part of the ElfScript Brigade team.
>
> This tool transforms Advent of Code into a CLI adventure

<img src="doc/logo/png/logo-color-small.png" alt="ElfScript Brigade Logo"/>

[![PyPI - Version](https://img.shields.io/pypi/v/esb.svg)](https://pypi.org/project/esb)[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/esb.svg)](https://pypi.org/project/esb)[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)

---

In the bureaucratic workshop of Santa's IT department, where the spirit of Christmas and the magic of coding converge, a special group of coding elves emerged known as the **ElfScript Brigade**. These skilled and whimsical elves were bestowed with the mission of safeguarding the joyous essence of Christmas through the power of scripting and coding.

`esb` is a CLI tool to help us _elves_ to save Christmas for the [Advent Of Code](https://adventofcode.com/) yearly events (Thank you [Eric 😉!](https://twitter.com/ericwastl)).

This tool allows us _elves_ to:

1. Fetch puzzle statement and puzzle data
2. Create language agnostic boilerplate code<sup>\*[Check supported languages](#currently-supported-languages)</sup>
3. Test run and submit solutions
4. Shiny dashboards
5. [Follows the rules of automation](#rules-of-automation)

## Table of Contents

- [Installation](##installation)
- [Usage](##usage)
- [Currently supported languages](#currently-supported-languages)
- [Dashboards](#dashboards)
- [FAQ](#faq)
- [Rules of Automation](#rules-of-automation)
- [License](##license)

## Installation

```shell
pip install esb
```

## Usage

> ### TLDR;
>
> ```shell
> mkdir my_aoc_repo && cd my_aoc_repo
>
> # Initializes ESB repo
> esb new
>
> # Create boilerplate code and fetches input data
> esb start --lang rust --year 2023 --day 13
>
> # Run code and submit answer
> esb run --lang rust --year 2023 --day 13 --submit
>
> # Collect stars!
> ```

### Initializing the repository

Create a `git` repository and initialize an `esb` repository too.

```shell
mkdir my_aoc_repo
cd my_aoc_repo
git init
esb new
git commit -m  "I now pledge to help, and I will forever help, saving christmas."
```

### Add your credentials

Set your credentials by locating your session cookie or save it in a `.env` file. If the cookie expires, you'll have to redo this step for fetching and submitting data.

@TODO: Show how to get the cookie

```shell
export AOC_SESSION_COOKIE="<my_current_cookie>"
# Or
echo "<my_current_cookie>" > .env
```

### Fetching problems

Downloads puzzle statement, data and correct answers (when applicable).

```shell
esb fetch --year 2016 --day 9

# Hint: Use brace expansion for fetching multiple days or years
esb fetch --year 2023 --day {1..25}
```

### Creating boilerplate code

Run `start` command to create code for the given language. It also fetches data if necessary

```shell
esb start --lang rust --year 2023 --day 13
```

### Running tests

Runs tests or selected tests

```shell
# Run all
esb test --all

# Run all from specific language
esb test --year 2016 --day 9 --lang rust --all

# Run single test
esb test --year 2016 --day 9 --lang rust --all
```

### Running for real

Runs the code for the given input. Also can submit solutions.

```shell
esb run --year 2016 --day 9 --lang rust

esb run --year 2016 --day 9 --lang rust --submit
```

### Check your progress in the command line

```shell
esb status
```

### The dashboards

The dashboards are created automatically when events happen. It's possible to generate
again by running:

```shell
esb dashboard
```

## Currently supported languages

Currently there are built in 3 supported languages. They set up the basic code for a
given day that allows `esb` to run and test solutions. Check the documentation
for each language and how to create your own boilerplate.

- Python
- Rust
- Elixir
- [_Create your own_](doc/FIREPLACEv1.0.md)

Any program that supports the [FIREPLACEv1](doc/FIREPLACEv1.0.md) prococol can use `esb` tooling.

## Dashboards

- Dash A
- Dash B

## FAQ

- **This tool is so stupid! I can hack my stats anytime I want!**

  > As _Acting Brigade Chief_, I have no powers nor will to enforce any regulatory actions against cheating. I leave this job to Santa's higher council and, of course, the guilt of leaving kids without their gifts.

- **Can I use this tool to bash the servers**

  > ## **No!**.

- **But, why python 3.11? What about my Debian friends?**

  > Because the developer wanted to some of the newest features



## Rules of Automation

ElfScript Brigade does follow the [automation guidelines](https://www.reddit.com/r/adventofcode/wiki/faqs/automation) on the [/r/adventofcode](https://www.reddit.com/r/adventofcode) community wiki
Specifically:

Once inputs are downloaded, they are cached locally in the `data` directory.
If you suspect your input is corrupted, you can manually request a fresh copy using `esb fetch ... --force`
The User-Agent header for the HTTP requests is set to me since I maintain this tool :)

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
> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
> GNU General Public License for more details.
> You should have received a copy of the GNU General Public License
> along with this program. If not, see <http://www.gnu.org/licenses/>.
