# Testing Solutions

ElfScript Brigade comes with a problem testing system and default tests from problem
statements. Additional tests may be created if necessary.

When calling `esb start` or `esb fetch` not only the problem is fetched but also all
the default test files for the current day at
[https://github.com/luxedo/esb/aoc_tests](https://github.com/luxedo/esb/aoc_tests).

## Default tests

These tests are created from problem statements, for example:

```
  # Advent of Code - 2016 day 01

  - Following R2, L3 leaves you 2 blocks East and 3 blocks North, or 5 blocks away.
  - R2, R2, R2 leaves you 2 blocks due South of your starting position, which is 2 blocks away.
  - R5, L5, R5, R3 leaves you 12 blocks away.
```

Gives the following test specification at `tests/2016/01/`:

```toml
#################################
#     Advent of Code Tests      #
#         Year: 2016            #
#           Day: 01             #
#################################
[test.test_01]
part = 1
input = "R2, L3"
answer = 5

[test.test_02]
part = 1
input = "R2, R2, R2"
answer = 2

[test.test_03]
part = 1
input = "R5, L5, R5, R3"
answer = 12
```

Calling `esb test` with the correct arguments will locate the test file and run the solution
for each test:

```shell
$ esb test --lang python --year 2016 --day 1 --part 1

Testing solution for: python, year 2016 day 01 part 1
✔ Answer tests_2016_01.test_01 pt1: 5
Testing solution for: python, year 2016 day 01 part 1
✔ Answer tests_2016_01.test_02 pt1: 2
Testing solution for: python, year 2016 day 01 part 1
✔ Answer tests_2016_01.test_03 pt1: 12
```

## Creating your tests

Test files are located on the `esb` repository `tests` directory.

```
tests
├── 2016
│   ├── 01
│   │   └── tests_2016_01.toml
│   ├── 02
│   │   └── tests_2016_02.toml
│   ├── 03
│   │   └── tests_2016_03.toml

...

```

Creating new tests is as easy as adding a new `toml` file to the corresponding year and
day to be tested. The relevant fields for each test in the file are `part`, `input` and
`answer`:

```toml
[test.test_03]             # Test name
part = 1                   # Which part to test
input = "R5, L5, R5, R3"   # Test input
answer = 12                # Expected output
```

Additionally, an `args` field might be necessary when the example tests run with different
parameters than the real input, check tests
[2022 day 15](../aoc_tests/2022/15/tests_2022_15.toml) for examples with `args`.
