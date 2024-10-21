"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

Script your way to rescue Christmas as part of the ElfScript Brigade team.

`esb` is a CLI tool to help us _elves_ to save christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from math import log10
from statistics import mean, median, stdev
from typing import TYPE_CHECKING

import plotext as plt  # type: ignore

from esb.config import ESBConfig
from esb.lib.paths import pad_day
from esb.protocol.metric_prefix import MetricPrefix

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Sequence
    from pathlib import Path
    from typing import Any, Self

    from esb.lib.db import ECAPuzzle, ECARun, ElvenCrisisArchive, Table
    from esb.lib.langs import LangMap

DayStars = dict[int, int]
YearStars = dict[int, DayStars]
LangStars = dict[str, YearStars]


@dataclass
class CorrectRun:
    year: int
    day: int
    part: int
    language: str
    time: float


@dataclass
class HTML:
    tag: str
    content: str = ""
    attributes: dict = field(default_factory=dict)
    children: list[Self] = field(default_factory=list)

    def add_child(self, child_element: Self) -> Self:
        self.children.append(child_element)
        return self

    def add_children(self, childrens: Iterable[Self]) -> Self:
        for child_element in childrens:
            self.add_child(child_element)
        return self

    def __str__(self) -> str:
        return self.render()

    def render(self, indent=0) -> str:
        indent_str = " " * indent
        attrs = " ".join(f'{key}="{value}"' for key, value in self.attributes.items())
        attrs_str = f" {attrs}" if attrs else ""
        if self.children or self.content:
            result = f"{indent_str}<{self.tag}{attrs_str}>"
            if self.content:
                result += f"{self.content}"
                result += "\n".join(child.render(indent=indent + 2) for child in self.children)
                result += f"</{self.tag}>"
            else:
                result += "\n"
                result += "\n".join(child.render(indent=indent + 2) for child in self.children)
                result += f"\n{indent_str}</{self.tag}>"
        else:
            result = f"{indent_str}<{self.tag}{attrs_str} />"
        return result


@dataclass
class BaseDash:
    db: ElvenCrisisArchive
    lmap: LangMap
    SOLVED_NONE: int = field(init=False, default=0)
    SOLVED_PT1: int = field(init=False, default=1)
    SOLVED_PT2: int = field(init=False, default=2)

    @staticmethod
    def groupby(rows: Iterable, key: str) -> dict[Any, Any]:
        ret: dict[Any, Any] = {}
        for row in rows:
            ret.setdefault(getattr(row, key), []).append(row)
        return ret

    @staticmethod
    def groupby_fn(rows: Iterable, fn: Callable) -> dict[Any, Any]:
        grouped_dates = defaultdict(list)
        for row in rows:
            month_name = fn(row)
            grouped_dates[month_name].append(row)
        return grouped_dates

    def count_stars(self, rows: Iterable, cmp: Callable[[Table], int]) -> YearStars:
        return {
            year: {day: cmp(s) for day, [s] in self.groupby(rows, "day").items()}
            for year, rows in self.groupby(rows, "year").items()
        }

    def fetch_year_stars(self) -> YearStars:
        stats = self.db.ECAPuzzle.fetch_all()

        def cmp_year(s):
            if s.day == ESBConfig.last_day and s.answer_pt1 is not None:  # Day 25 has only one star
                return self.SOLVED_PT2
            return (
                self.SOLVED_NONE
                if s.answer_pt1 is None
                else self.SOLVED_PT1
                if s.answer_pt2 is None
                else self.SOLVED_PT2
            )

        return self.count_stars(stats, cmp_year)

    def fetch_lang_stars(self) -> LangStars:
        langs = self.db.ECALanguage.fetch_all()

        def cmp_lang(s):
            return int(s.solved_pt1 is not None) + int(s.solved_pt2 is not None)

        return {lang: self.count_stars(rows, cmp_lang) for lang, rows in self.groupby(langs, "language").items()}

    @staticmethod
    def build_year_str(year: int, days: DayStars) -> str:
        solved_all = (
            all(v == ESBConfig.max_parts for v in days.values()) and len(set(days.keys())) == ESBConfig.last_day
        )
        return f"[yellow]* {year}[/yellow]" if solved_all else f"[yellow]  {year}[/yellow]"

    @staticmethod
    def build_stars_str(days: DayStars, symbol: str) -> str:
        ret = []
        for day in range(1, 26):
            solved = days.get(day, 0)
            unsolved = ESBConfig.max_parts - solved
            ret.append("".join([symbol] * solved + [" "] * unsolved))
        return " ".join(ret)

    def build_lang_stars_str(self, lang_stars: LangStars, year: int) -> str:
        ret = ""
        for lang in sorted(lang_stars.keys()):
            match lang_stars[lang].get(year, {}):
                case {**keys} if not keys:
                    continue
                case stars:
                    ret += self.build_stars_str(stars, self.lmap.get(lang).symbol)
        return ret

    def brigadista(self) -> str:
        b = self.db.ECABrigadista.fetch_single()
        return f"* Brigadista ID: {b.brigadista_id}\n* In Duty Since: {b.creation_date}"

    @staticmethod
    def strip_ansi(text: str) -> str:
        ansi_escape = re.compile(r"(\x9B|\x8F|\x9A|\x8D|\x90|(?:\x1B\[|\x1B\])[0-9;]*m)")
        return ansi_escape.sub("", text)

    @staticmethod
    def sort_dict_by_value(d: dict, *, ascending=True) -> dict:
        s = 1 if ascending else -1
        return dict(sorted(d.items(), key=lambda item: s * item[1]))

    @staticmethod
    def sort_dict_by_key(d: dict, *, ascending=True) -> dict:
        s = 1 if ascending else -1
        return dict(sorted(d.items(), key=lambda item: s * item[0]))

    def fill_years(self, years_dict):
        min_year = min(years_dict)
        max_year = max(years_dict)
        for year in range(min_year, max_year):
            years_dict[year] = years_dict.get(year, 0)
        return self.sort_dict_by_key(years_dict, ascending=False)

    def fill_months(self, month_dict):
        min_month = min(datetime.strptime(month, "%Y-%m") for month in month_dict)  # noqa: DTZ007
        max_month = max(datetime.strptime(month, "%Y-%m") for month in month_dict)  # noqa: DTZ007
        current_date = min_month
        while current_date <= max_month:
            month_str = current_date.strftime("%Y-%m")
            month_dict[month_str] = month_dict.get(month_str, 0)
            current_date = (current_date + timedelta(days=32)).replace(day=1)
        return self.sort_dict_by_key(month_dict)

    @staticmethod
    def plt_remove_trailing_zeros(plt_str: str) -> str:
        return re.sub(r"\.0$", "", plt_str, flags=re.MULTILINE)

    @staticmethod
    def histogram(data, bins=10):
        min_value = min(data)
        max_value = max(data)
        bin_width = (max_value - min_value) / bins

        bins_edges = [min_value + bin_width * i for i in range(bins + 1)]
        counts = [0] * bins

        for value in data:
            bin_index = int((value - min_value) // bin_width)
            if bin_index >= 0 and bin_index < len(counts):
                counts[bin_index] += 1

        return counts, bins_edges

    def log_histogram(self, data, bins=10):
        data = [log10(d) for d in data]
        counts, bins_edges = self.histogram(data, bins)
        return counts, bins_edges

    def correct_runs(self, runs: Sequence[ECARun], puzzles: Sequence[ECAPuzzle]) -> Sequence[CorrectRun]:
        puzzles_group = {
            year: {day: puzzle for day, [puzzle] in self.groupby(puzzles_year, "day").items()}
            for year, puzzles_year in self.groupby(puzzles, "year").items()
        }
        runs_group = {year: self.groupby(runs_year, "day") for year, runs_year in self.groupby(runs, "year").items()}
        return [
            CorrectRun(year, day, run.part, run.language, run.unit.to_float(run.time))
            for year, runs_year in runs_group.items()
            for day, runs_day in runs_year.items()
            for run in runs_day
            if (run.time is not None)
            and (
                ((run.part == ESBConfig.part_1) and run.answer == puzzles_group[year][day].answer_pt1)
                or ((run.part == ESBConfig.part_2) and run.answer == puzzles_group[year][day].answer_pt2)
            )
        ]

    def plots(self, *, times_tables: bool = False) -> str:
        no_data = "\n-- No data --\n"
        not_enough_data = "\n-- Not enough data. Run more solutions --\n"
        summary_msg = ""

        # AoC Solves
        puzzles = list(self.db.ECAPuzzle.fetch_all())
        puzzles_group = self.groupby(puzzles, "year")
        solves_per_year = {
            year: len([puzzle for puzzle in puzzles if puzzle.solved_pt2 is not None])
            for year, puzzles in puzzles_group.items()
        }
        if len(solves_per_year) != 0:
            solves_per_year = self.fill_years(solves_per_year)
            plt.simple_bar(solves_per_year.keys(), solves_per_year.values(), width=80, title="AoC Solves")
            solves_per_year_plot = self.strip_ansi(plt.build())
            solves_per_year_plot = self.plt_remove_trailing_zeros(solves_per_year_plot)
        else:
            solves_per_year_plot = no_data

        # Favorite language
        languages = list(self.db.ECALanguage.fetch_all())
        languages_group = self.groupby(languages, "language")
        solves_per_language = {
            lang: len([puzzle for puzzle in puzzles if puzzle.solved_pt2 is not None])
            for lang, puzzles in languages_group.items()
        }
        if len(solves_per_language) != 0:
            solves_per_language = self.sort_dict_by_value(solves_per_language, ascending=False)
            plt.simple_bar(
                solves_per_language.keys(), solves_per_language.values(), width=80, title="Favorite languages"
            )
            solves_per_language_plot = self.strip_ansi(plt.build())
            solves_per_language_plot = self.plt_remove_trailing_zeros(solves_per_language_plot)
        else:
            solves_per_language_plot = no_data

        # Solve time per year
        year_plots = ""
        runs = list(self.db.ECARun.fetch_all())
        correct = self.correct_runs(runs, puzzles)
        year_times = self.sort_dict_by_key(
            {year: [r.time for r in runs] for year, runs in self.groupby(correct, "year").items()}, ascending=False
        )
        time_ticks = [-7.5, -6, -4.5, -3, -1.5, 0, 1.5, 3, 4.5]
        time_labels = [MetricPrefix.format_float(10**i, "s", precision=0, short=True) for i in time_ticks]
        base_width = len(time_ticks)
        min_stats_points = 3
        for year, times in year_times.items():
            plt.clear_figure()
            if len(times) < min_stats_points:
                year_plots += f"{not_enough_data}\n\n"
                continue
            hist, edges = self.log_histogram(times, bins=base_width)
            plt.bar(edges, hist)
            plt.plot_size(base_width * 9, 20)
            plt.xlim(min(time_ticks), max(time_ticks))
            plt.xticks(time_ticks, time_labels)
            times_mean = mean(times)
            times_stdev = stdev(times)
            times_median = median(times)
            times_mean_str = MetricPrefix.format_float(times_mean, "s", precision=3, short=True)
            times_stdev_str = MetricPrefix.format_float(times_stdev, "s", precision=3, short=True)
            times_median_str = MetricPrefix.format_float(times_median, "s", precision=3, short=True)
            plt.vline(log10(times_mean))
            plt.vline(log10(times_median))
            plt.title(f"Year {year} - mean: {times_mean_str}; stdev: {times_stdev_str}; median: {times_median_str}")
            year_time_plot = self.strip_ansi(plt.build())
            year_plots += f"{year_time_plot}\n\n"

        if not year_plots:
            year_plots = no_data

        detailed_times = self.sort_dict_by_key(
            {
                year: {day: [r.time for r in runs] for day, runs in self.groupby(year_runs, "day").items()}
                for year, year_runs in self.groupby(correct, "year").items()
            },
            ascending=False,
        )
        detailed_plots = ""
        for year, year_runs in detailed_times.items():
            plt.clear_figure()
            plt.plot_size(base_width * 9.3, 20)
            plt.title(f"Year {year}")
            plt.xlim(0, ESBConfig.last_day)
            plt.xticks(range(1, 26))
            plt.ylim(min(time_ticks), max(time_ticks))
            plt.yticks(time_ticks, time_labels)

            run_data = [
                (day, mean(times), stdev(times)) for day, times in year_runs.items() if len(times) >= min_stats_points
            ]
            days, day_means, day_means_log, day_std = list(
                zip(*[(d, ts, log10(ts), std) for d, ts, std in run_data], strict=False)
            )
            plt.scatter(days, day_means_log)
            detailed_plots += f"\n```\n{self.strip_ansi(plt.build())}\n```\n"

            if times_tables:
                mean_map = dict(
                    zip(
                        days,
                        (MetricPrefix.format_float(m, "s", precision=3, short=True) for m in day_means),
                        strict=False,
                    )
                )
                std_map = dict(
                    zip(
                        days,
                        (MetricPrefix.format_float(m, "s", precision=3, short=True) for m in day_std),
                        strict=False,
                    )
                )

                rows = []
                columns = [range(i, i + 5) for i in range(1, 26, 5)]
                for s in columns:
                    rows.extend([
                        HTML("tr")
                        .add_child(HTML("th", content="day"))
                        .add_children([HTML("th", content=pad_day(i)) for i in s]),
                        HTML("tr")
                        .add_child(HTML("td", content="mean"))
                        .add_children([HTML("td", content=mean_map.get(i, "--")) for i in s]),
                        HTML("tr")
                        .add_child(HTML("td", content="std"))
                        .add_children([HTML("td", content=std_map.get(i, "--")) for i in s]),
                        HTML("tr").add_child(HTML("td", attributes={"colspan": 7})),
                    ])
                table = HTML("table").add_children(rows)
                detailed_plots += f"\n{table!s}\n"
        summary_msg += (
            "## General Statistics\n"
            f"```\n"
            f"{solves_per_year_plot}\n"
            f"{solves_per_language_plot}\n"
            f"```\n"
            "\n## Solutions timing\n"
            f"```\n"
            f"{year_plots.rstrip()}\n"
            "```\n"
            "\n## Detailed Running times\n"
            f"{detailed_plots}\n"
        )

        return summary_msg


@dataclass
class CliDash(BaseDash):
    full: bool

    def years_summary(self) -> dict[int, str]:
        year_stars = self.fetch_year_stars()
        lang_stars = self.fetch_lang_stars()

        ret = {}
        for year, days in year_stars.items():
            year_title = self.build_year_str(year, days)
            langs_str = self.build_lang_stars_str(lang_stars, year)
            stars_str = f'[yellow]{self.build_stars_str(days, "*")}[/yellow]'
            days_str = " ".join([f"{pad_day(day)}" for day in range(1, 26)])
            sep_str = f'[yellow]{"=".join(["==" for _ in range(1, 26)])}[/yellow]'
            ret[year] = f"{year_title}\n{langs_str}\n{stars_str}\n{days_str}\n{sep_str}\n"
        return ret

    def working_on(self) -> str:
        ac = self.db.ECAArgCache.fetch_single()
        return f"= Working on: {ac.language}, {ac.year} day {ac.day} part {ac.part} ="

    def build_dash(self) -> str:
        report = ""
        brigadista = self.brigadista()
        working_on = self.working_on()
        report += "[bold red]ELFSCRIPT BRIGADE STATUS REPORT[/bold red]\n\n"
        report += f"{working_on}\n\n"
        report += f"{brigadista}\n\n"
        report += "SERVICE STARS\n"

        ys = self.years_summary()
        for year in sorted(ys.keys(), reverse=True):
            report += f"\n{ys[year]}"

        if self.full:
            report += "\n\n[bold red]ELFSCRIPT BRIGADE TECHNICAL REPORT[/bold red]\n\n"
            report += self.plots().replace("```\n", "")

        return report


@dataclass
class MdDash(BaseDash):
    repo_root: Path
    readme: Path = field(init=False)
    report: Path = field(init=False)
    start_tag: str = "<!-- Do not delete - Report start -->"
    end_tag: str = "<!-- Do not delete - Report end -->"

    def __post_init__(self):
        self.readme = self.repo_root / "README.md"
        self.report = self.repo_root / "REPORT.md"

    def build_dash(self, *, reset: bool) -> str:
        template = ESBConfig.blank_dash.read_text() if reset else self.readme.read_text()
        self.validate_tags(template)

        years_summary_str = ""
        ys = self.years_summary()
        for year in sorted(ys.keys(), reverse=True):
            years_summary_str += f"\n{ys[year]}"

        brigadista = self.brigadista()
        summary_msg = f"{brigadista}\n" "\n## SERVICE STARS\n" f"{years_summary_str}\n"

        final_text = self.paste_text(template, summary_msg)
        self.readme.write_text(final_text)
        return final_text

    def build_report(self, *, reset: bool) -> str:
        template = ESBConfig.blank_report.read_text() if reset else self.report.read_text()
        self.validate_tags(template)

        brigadista = self.brigadista()
        plots_str = self.plots(times_tables=True)

        report_msg = f"{brigadista}\n\n{plots_str}"

        final_text = self.paste_text(template, report_msg)
        self.report.write_text(final_text)
        return final_text

    def validate_tags(self, template: str):
        if self.start_tag not in template:
            message = "Could not find start tag in the markdown file"
            raise ValueError(message)

        if self.end_tag not in template:
            message = "Could not find end tag in the markdown file"
            raise ValueError(message)

    def paste_text(self, template: str, msg: str) -> str:
        start_idx = template.index(self.start_tag)
        end_idx = template.index(self.end_tag)

        return template[: start_idx + len(self.start_tag) + 1] + msg + template[end_idx:]

    def years_summary(self) -> dict[int, str]:
        year_stars = self.fetch_year_stars()
        lang_stars = self.fetch_lang_stars()

        ret = {}
        for year, days in year_stars.items():
            columns = [range(i, i + 6) for i in range(1, 25, 6)]
            rows = [row for s in columns for row in self.build_stars_row(year, days, lang_stars, s)]
            last_day_rows = list(
                self.build_stars_row(
                    year, days, lang_stars, [ESBConfig.last_day], td_attributes={"colspan": 6, "align": "center"}
                )
            )
            last_day_rows.pop()
            table = HTML("table").add_children(rows).add_children(last_day_rows)

            solved = [v == ESBConfig.max_parts for v in days.values()]
            year_title = f"### {year} ({sum(solved)}/{ESBConfig.last_day})"
            if all(solved) and len(set(days.keys())) == ESBConfig.last_day:
                year_title += " ⭐"

            ret[year] = f"\n{year_title}\n\n" f"{table!s}"
        return ret

    def build_stars_row(
        self,
        year: int,
        days: dict[int, int],
        lang_stars: LangStars,
        subset: Iterable[int],
        td_attributes: dict[str, Any] | None = None,
    ) -> Iterable[HTML]:
        td_attributes = {} if td_attributes is None else td_attributes
        lang_stars_str = [
            "⭐⭐" if days.get(day) == self.SOLVED_PT2 else "⭐☆" if days.get(day) == self.SOLVED_PT1 else "☆ ☆"
            for day in subset
        ]
        return [
            *self.build_lang_rows(year, lang_stars, subset, td_attributes),
            HTML("tr").add_children([HTML("td", content=stars, attributes=td_attributes) for stars in lang_stars_str]),
            HTML("tr").add_children([
                HTML("th", content=f"{pad_day(day)}", attributes=td_attributes) for day in subset
            ]),
            HTML("tr").add_child(HTML("td", attributes={"colspan": len(list(subset)), **td_attributes})),
        ]

    def build_lang_rows(
        self, year: int, lang_stars: LangStars, subset: Iterable[int], td_attributes: dict[str, Any] | None = None
    ) -> Iterable[HTML]:
        td_attributes = {} if td_attributes is None else td_attributes
        langs = []
        for lang, years in lang_stars.items():
            if year not in years or sum(years[year].values()) == 0:
                continue
            emoji = self.lmap.get(lang).emoji
            lang_star_map = {
                day: f"{emoji}{emoji}"
                if stars == self.SOLVED_PT2
                else f"{emoji} ☐"
                if stars == self.SOLVED_PT1
                else "☐ ☐"
                for day, stars in years[year].items()
            }
            lang_row = [HTML("td", content=lang_star_map.get(day, "☐ ☐"), attributes=td_attributes) for day in subset]
            langs.append(HTML("tr").add_children(lang_row))
        return langs
