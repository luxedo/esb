"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

ESB - Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from esb.langs import LangSpec


@dataclass
class CodeFurnace:
    spec: LangSpec


# def prepare_template(spec: LanguageSpec, year: int, day: int, cookie: str):
#     def process_title(description_pt1: str, day: int) -> str:
#         punc = "".join(p for p in punctuation if p != "_")
#         return (
#             description_pt1.split("\n")[0]
#             .replace("-", "")
#             .replace(":", "")
#             .strip()
#             .lower()
#             .replace(" ", "_")
#             .replace(f"day_{day}", f"day_{day:02}")
#             .translate(str.maketrans("", "", punc))
#         )
#
#     def copy_replace_recursive(src: Path, dst: Path, year: int):
#         if not dst.is_dir():
#             dst.mkdir(parents=True, exist_ok=True)
#         for f in src.iterdir():
#             if f.is_dir():
#                 copy_replace_recursive(f, dst.joinpath(f.name), year)
#             else:
#                 with f.open() as fp:
#                     contents = fp.read().replace("{year}", str(year))
#                 with dst.joinpath(f.name).open("w") as fp:
#                     fp.write(contents)
#
#     def prepare_project(spec: LanguageSpec, year: int):
#         project_dir = spec.destination(year)
#         if not project_dir.is_dir():
#             if spec.project_base is not None:
#                 print(f"Creating project base at {project_dir}...")
#                 copy_replace_recursive(spec.project_base, project_dir, year)
#             template_destination = spec.template_destination(year)
#             if not template_destination.is_dir():
#                 template_destination.mkdir(parents=True, exist_ok=True)
#
#     def prepare_main_template(
#         spec: LanguageSpec, year: int, day: int, title: str, description_pt1: str
#     ):
#         template = spec.root.joinpath(spec.template)
#         filename = spec.executable(year, day)
#         if filename.is_file():
#             print(f"Main {filename} already exists. Skipping...")
#             return
#         print(f"Creating template for {filename}...")
#         with open(template, "r", encoding="utf-8") as fp:
#             full_url = f"https://{HOST}{route}"
#             bp = (
#                 fp.read()
#                 .replace("{url}", full_url)
#                 .replace("{description_pt1}", description_pt1)
#                 .replace("{year}", f"{year}")
#                 .replace("{day}", f"{day:02}")
#             )
#             if PT2_ANCHOR in bp:
#                 bp = "\n".join(
#                     [line for line in bp.split("\n") if "{description_pt2}" not in line]
#                 )
#         with open(filename, "w", encoding="utf-8") as fp:
#             fp.write(bp)
#
#     def prepare_test_template(spec: LanguageSpec, year: int, day: int):
#         template = spec.root.joinpath(spec.test_template)
#         filename = spec.test_executable(year, day)
#         if filename.is_file():
#             print(f"Test {filename} already exists. Skipping...")
#             return
#         print(f"Creating template for {filename}...")
#         with open(template, "r", encoding="utf-8") as fp:
#             full_url = f"https://{HOST}{route}"
#             bp = (
#                 fp.read()
#                 .replace("{url}", full_url)
#                 .replace("{year}", f"{year}")
#                 .replace("{day}", f"{day:02}")
#             )
#         with open(filename, "w", encoding="utf-8") as fp:
#             fp.write(bp)
#
#     def prepare_input(spec: LanguageSpec, year: int, day: int):
#         filename = spec.input(year, day)
#         data_dir = filename.parent
#         if not data_dir.is_dir():
#             data_dir.mkdir(parents=True, exist_ok=True)
#
#         if filename.is_file():
#             print(f"Input {filename} already exists. Skipping...")
#             return
#
#         print(f"Fetching input data: {filename}")
#         problem_data = fetch_url(INPUT_URL.format(year=year, day=day), cookie)
#         with open(filename, "w") as fp:
#             fp.write(problem_data)
#
#     route = ROUTE.format(year=year, day=day)
#     body = fetch_url(route, cookie)
#     description_pt1 = parse_body(body)
#     title = process_title(description_pt1, day)
#     prepare_project(spec, year)
#     prepare_main_template(spec, year, day, title, description_pt1)
#
#     prepare_input(spec, year, day)
#
#     if spec.test_template:
#         prepare_test_template(spec, year, day)
#
#
