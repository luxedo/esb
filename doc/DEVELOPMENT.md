# Development Guidelines

This document outlines the development process for the ESB (ElfScript Brigade) project, a CLI tool for Advent of Code.

## Prerequisites:

- Python 3.11 (or later)
- Familiarity with Python development
- [Hatch](https://github.com/pypa/hatch)

## Getting Started:

Clone the Repository:

```shell
git clone https://github.com/luxedo/esb.git
cd esb
```

## Install Project:

After cloning and entering the project's directory, install

```shell
hatch shell
pip install -e .
```

## Running Tests:

To run the entire test suite chose from:

```shell
# Run all tests
hatch test

# or

# Run tests and show code coverage
hatch run cov
```

It's possible to run tests with pytest:

```shell
pytest <filename>

# or

pytest -m <test-name>
```

## Testing Manually:

For manual tests an `esb` repo is needed. To do so, call `esb init` on an empty directory
and run the commands manually:

```shell
# Inside a hatch shell

cd ..
mkdir my_esb_repo
cd my_esb_repo
esb init

# Run commands ...
```

## Coding standards:

Coding standards are enforced with [Ruff](https://docs.astral.sh/ruff/) and
[MyPy](https://mypy-lang.org/) in the CI pipeline. There's a [pre-commit](https://pre-commit.com/)
pipeline configured as well. If you wish to run the pipeline call:

```shell
# Install the pre commit hook (optional)
pre-commit install

# Run the pipeline manually
pre-commit run --all
```

## Thank you!

Feel free to open issues on GitHub for bug reports or feature requests.
We appreciate your contribution to the ElfScript Brigade!
