# ESB Boilerplates

A language boilerplate is the blueprint for creating AoC solutions. Creating a new boilerplate involves building the following structure inside a directory:

1. `spec.json` which describes the boilerplate properties.
2. `template/` directory, which contains files that can be changed given [template tags](#template-tags).
3. `base/` directory, which contains static files (optional)

As an example, the following python template has all three essential components:

```
python
├── spec.json
├── base
│   └── requirements.txt
└── template
    └── main.py
```

## Boilerplate Files

### `spec.json`

The `spec.json` describes the boilerplate properties and how to copy it to the destination directory.

Eg:

```json
{
  "name": "elixir",
  "files": {
    "lib/main.ex": "lib/aoc_{year}_{day}.ex"
  },
  "run_command": ["mix", "run", "-e", "Year{year}Day{day}.start", "--"],
  "symbol": "[purple]e[/purple]",
  "emoji": "⚗️",
  "base": true,
  "build_command": ["mix", "compile"],
  "install": ["mix", "deps.get"]
}
```

#### `spec.json` properties

- `name`: Language name.
- `files`: A mapping from source in `template` directory to destination. This is useful for renaming
  files. `template` files not listed in `files` are copied without renaming.
- `run_command`: Command used to run the program.
- `symbol`: Symbol used to represent the language in `esb status`. Formatted with [rich](https://rich.readthedocs.io/)
- `emoji`: Emoji used for markdown reports.
- `base`: Boolean representing whether to copy files in `base` directory or not.
- `build_command`: Command used to build the solutions.
- `install`: Command that runs only after the boilerplate is copied.

## `template` directory

The `template` directory contains the files to be copied. In this example, it's just a python module, but it might be a full project for any language.

### Template Tags

All files in `template` are formatted by adding the following field values into the files:

- `{year}`: Problem year
- `{day}`: Problem day
- `{language}`: Selected language
- `{problem_title}`: Problem title
- `{problem_url}`: Problem url

Eg:

```python
"""
ElfScript Brigade

Advent Of Code {year} Day {day}
Python Solution

{problem_title}

https://{problem_url}
"""

def solve_pt1(input_data: str, args: list[str] | None = None) -> int:
    ...

def solve_pt2(input_data: str, args: list[str] | None = None) -> int:
    ...

if __name__ == "__main__":
    from esb.protocol import fireplace
    # 🎅🎄❄️☃️🎁🦌
    # Bright christmas lights HERE
    fireplace.v1_run(solve_pt1, solve_pt2)
```

For year 2016 and day 2 will become:

```python
"""
ElfScript Brigade

Advent Of Code 2016 Day 02
Python Solution

Day 2: Bathroom Security

https://adventofcode.com/2016/day/2
"""

def solve_pt1(input_data: str, _args: list[str] | None = None) -> str:
    ...

def solve_pt2(input_data: str, _args: list[str] | None = None) -> str:
    ...

if __name__ == "__main__":
    from esb.protocol import fireplace
    # 🎅🎄❄️☃️🎁🦌
    # Bright christmas lights HERE
    fireplace.v1_run(solve_pt1, solve_pt2)
```

## `base` directory

By setting `"base": true` in `spec.json` it's possible to copy additional files
into the destination directory.

## Testing boilerplate creation

For testing, the flag `-f` for `esb start` is very useful when overwriting the files.

```console
esb start --year 2016 --day 13 --lang <path_to_spec> -f
```

Sometimes the destination files become messy when developing a new boilerplate. Remember to
clean the testing directory with:

```console
rm -r solutions/python/2016/13
```

With esb at your fingertips, the ElfScript Brigade empowers you to streamline your Advent of
Code journey. This tool, crafted with the holiday spirit and a dash of automation magic,
helps you conquer festive coding challenges with ease. Leverage pre-built boilerplates,
automate mundane tasks, and track your progress with festive dashboards – all while upholding
the spirit of fair competition. So, don your coding hat, embrace the challenge, and let esb
be your trusty elf companion in the quest for Advent of Code glory!
