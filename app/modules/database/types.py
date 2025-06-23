"""
Annotated types for usage with Mapped[]
"""

import sqlalchemy as orm

from datetime import datetime, date
from typing_extensions import Annotated
from sqlalchemy.orm import mapped_column, DeclarativeBase


class Ints:
    Serial = Annotated[int, orm.Sequence(start=0, increment=1, name='Sequence'), mapped_column(orm.BIGINT, primary_key=True)]
    Long = Annotated[int, mapped_column(orm.BIGINT, nullable=False)]
    Short = Annotated[int, mapped_column(orm.SMALLINT, nullable=False)]
    Int = Annotated[int, mapped_column(orm.INTEGER, nullable=False)]


class FixedStrings:
    Char16 = Annotated[str, mapped_column(orm.CHAR(16), nullable=False)]
    Char32 = Annotated[str, mapped_column(orm.CHAR(32), nullable=False)]
    Char64 = Annotated[str, mapped_column(orm.CHAR(64), nullable=False)]
    Char128 = Annotated[str, mapped_column(orm.CHAR(128), nullable=False)]
    Char256 = Annotated[str, mapped_column(orm.CHAR(256), nullable=False)]


class VarStrings:
    Char16 = Annotated[str, mapped_column(orm.VARCHAR(16), nullable=False)]
    Char32 = Annotated[str, mapped_column(orm.VARCHAR(32), nullable=False)]
    Char64 = Annotated[str, mapped_column(orm.VARCHAR(64), nullable=False)]
    Char128 = Annotated[str, mapped_column(orm.VARCHAR(128), nullable=False)]
    Char256 = Annotated[str, mapped_column(orm.VARCHAR(256), nullable=False)]


class FloatingPoint:
    Double = Annotated[float, mapped_column(orm.DOUBLE, nullable=False)]
    Float = Annotated[float, mapped_column(orm.FLOAT, nullable=False)]


class Datetime:
    Datetime = Annotated[datetime, mapped_column(orm.TIMESTAMP, nullable=False, default=orm.func.current_timestamp())]
    DatetimeEmpty = Annotated[datetime, mapped_column(orm.TIMESTAMP, nullable=True, default=None)]
    Date = Annotated[date, mapped_column(orm.DATE, nullable=False)]


class ModelBase(DeclarativeBase):
    ...
