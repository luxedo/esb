"""
SPDX-FileCopyrightText: 2024-present Luiz Eduardo Amaral <luizamaral306@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later

Script your way to rescue Christmas as part of the ElfScript Brigade team.

`info` is a CLI tool to help us _elves_ to store christmas for the
[Advent Of Code](https://adventofcode.com/) yearly events
(Thank you [Eric 😉!](https://twitter.com/ericwastl)).
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator
    from datetime import datetime
    from typing import ClassVar, Self


###########################################################
# Db Base
###########################################################
class Singleton(type):
    """
    Metaclass for creating singletons.

    Every derived class must implement a check method that is always called to verify if the
    arguments received by the derived class are not changing expected behavior
    """

    _instances: ClassVar[dict[type, type]] = {}

    def __call__(cls, *args, **kwargs) -> type:
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        cls.check(*args, **kwargs)
        return cls._instances[cls]

    @classmethod
    def clear_instances(cls):
        for instance in cls._instances:
            instance.clear()
        cls._instances = {}

    @classmethod
    def check(cls, *args, **kwargs):  # noqa ARG003
        message = "This method should be implemented by derived classes"
        raise NotImplementedError(message)

    def clear(cls):
        message = "This method should be implemented by derived classes"
        raise NotImplementedError(message)


class SqlConnection(metaclass=Singleton):
    """
    Sql Connection singleton

    Initializes once with an optional
    """

    db_path: str

    def __init__(self, db_path: str | None):
        if db_path is not None:
            self.db_path = db_path
        self.con = sqlite3.connect(self.db_path)
        self.cur = self.con.cursor()

    @classmethod
    def check(cls, *args, **kwargs):
        match args, kwargs:
            case ((db_path,), {}) | (tuple(), {"db_path": db_path}):
                if not hasattr(cls, "db_path"):
                    cls.db_path = db_path
                if db_path != cls.db_path:
                    message = "Cannot change db_path after initialization"
                    raise ValueError(message)
            case (tuple(), {}):
                pass
            case _:
                message = f"Class {cls.__name__} receives only one or zero arguments"
                raise ValueError(message)

    @classmethod
    def clear(cls):
        delattr(cls, "db_path")

    def list_all_tables(self) -> list[tuple[str, ...]]:
        return self.cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()


class Table:
    _sql: SqlConnection

    @staticmethod
    def inject_sql_connection(fn):
        def wrapper(cls, *args, **kwargs):
            if not hasattr(cls, "_sql"):
                cls._sql = SqlConnection()
            return fn(cls, *args, **kwargs)

        return wrapper

    @classmethod
    def build_class(cls, row: tuple) -> Self:
        return cls(**dict(zip(cls.__annotations__.keys(), row)))

    @classmethod
    @inject_sql_connection
    def fetch_all(cls) -> Iterator[Self]:
        query = f"SELECT * FROM {cls.__name__}"  # noqa: S608
        cls._sql.cur.execute(query)
        for row in cls._sql.cur.fetchall():
            yield cls.build_class(row)

    @classmethod
    @inject_sql_connection
    def fetch_one(cls) -> Self:
        query = f"SELECT * FROM {cls.__name__} LIMIT 1"  # noqa: S608
        cls._sql.cur.execute(query)
        row = cls._sql.cur.fetchone()
        return cls.build_class(row)

    @classmethod
    @inject_sql_connection
    def fetch_single(cls) -> Self:
        query = f"SELECT COUNT(*) FROM {cls.__name__}"  # noqa: S608
        cls._sql.cur.execute(query)
        (rows,) = cls._sql.cur.fetchone()
        if rows != 1:
            message = f"Table {cls.__name__} should have one row and one row only. Got {rows}. Something is wrong."
            raise RuntimeError(message)
        return cls.fetch_one()

    @classmethod
    @inject_sql_connection
    def find(cls, match: dict) -> Iterator[Self]:
        where = " AND ".join(f"{column} = '{value}'" for column, value in match.items())
        query = f"SELECT * FROM {cls.__name__} WHERE {where}"  # noqa: S608
        cls._sql.cur.execute(query)
        for row in cls._sql.cur.fetchall():
            yield cls.build_class(row)

    @classmethod
    @inject_sql_connection
    def find_one(cls, match: dict) -> Self | None:
        where = " AND ".join(f"{column} = '{value}'" for column, value in match.items())
        query = f"SELECT * FROM {cls.__name__} WHERE {where} LIMIT 1"  # noqa: S608
        cls._sql.cur.execute(query)
        match cls._sql.cur.fetchone():
            case None:
                return None
            case row:
                return cls.build_class(row)

    @classmethod
    @inject_sql_connection
    def find_single(cls, match: dict) -> Self | None:
        where = " AND ".join(f"{column} = '{value}'" for column, value in match.items())
        query = f"SELECT COUNT(*) FROM {cls.__name__} WHERE {where}"  # noqa: S608
        cls._sql.cur.execute(query)
        (rows,) = cls._sql.cur.fetchone()
        if rows > 1:
            message = f"Table {cls.__name__} should have found one or zero rows. Got {rows}. Something is wrong."
            raise RuntimeError(message)
        return cls.find_one(match)

    @inject_sql_connection
    def insert(self):
        columns = self.__annotations__.keys()
        columns_query = ", ".join(columns)
        placeholders = ", ".join(["?" for _ in columns])
        values = tuple(getattr(self, column) for column in columns)
        query = f"INSERT INTO {self.__class__.__name__} ({columns_query}) VALUES ({placeholders})"  # noqa: S608
        self._sql.cur.execute(query, values)
        self._sql.con.commit()

    @inject_sql_connection
    def update(self):
        pass
        # columns = self.__annotations__.keys()
        # columns_query = ", ".join(columns)
        # placeholders = ", ".join(["?" for _ in columns])
        # values = tuple(getattr(self, column) for column in columns)
        # query = f"INSERT INTO {self.__class__.__name__} ({columns_query}) VALUES ({placeholders})"
        # self._sql.cur.execute(query, values)
        # self._sql.con.commit()

    @inject_sql_connection
    def insert_or_replace(self):
        columns = self.__annotations__.keys()
        columns_query = ", ".join(columns)
        placeholders = ", ".join(["?" for _ in columns])
        values = tuple(getattr(self, column) for column in columns)
        query = f"INSERT OR REPLACE INTO {self.__class__.__name__} ({columns_query}) VALUES ({placeholders})"  # noqa: S608
        self._sql.cur.execute(query, values)
        self._sql.con.commit()


###########################################################
# Tables and Data Types
###########################################################
@dataclass
class BrigadistaInfo(Table):
    brigadista_id: str
    creation_date: datetime


@dataclass
class SolutionStatus(Table):
    year: int
    day: int
    pt1_answer: str | None
    pt2_answer: str | None


class Tables:
    tables: ClassVar[dict[type[Table], str]] = {
        BrigadistaInfo: """CREATE TABLE {table_name} (
                                brigadista_id CHARACTER(36),
                                creation_date TIMESTAMP NOT NULL
                            )""",
        SolutionStatus: """CREATE TABLE {table_name} (
                                year INTEGER NOT NULL,
                                day INTEGER NOT NULL,
                                pt1_answer TEXT,
                                pt2_answer TEXT,
                                PRIMARY KEY (year, day)
                            )""",
    }

    @classmethod
    def create_tables(cls):
        sql = SqlConnection()
        for _cls, create_table_query in cls.tables.items():
            sql.cur.execute(create_table_query.format(table_name=_cls.__name__))


###########################################################
# Main DB Interface
###########################################################
class ElvenCrisisArchive:
    db_path = "data/ElvenCrisisArchive.db"

    def __init__(self):
        self.sql = SqlConnection(self.db_path)
        self.Tables = Tables
        self.BrigadistaInfo = BrigadistaInfo
        self.SolutionStatus = SolutionStatus

    @classmethod
    def has_db(cls):
        return Path(cls.db_path).is_file()
