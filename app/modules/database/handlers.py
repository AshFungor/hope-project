# sql alchemy
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

import sqlalchemy
import sqlalchemy.orm

# typing extensions
import typing_extensions

# local
from app.env import env

# default
from typing import Union

import datetime
import urllib.parse
import logging
import enum


class DatabaseType(enum.IntEnum):
    SQL_LITE = 1
    POSTGRES = 2
    MOCK = 3

    @staticmethod
    def from_str(string: str) -> Union[enum.IntEnum, None]:
        mappings = {
            'postgres': DatabaseType.POSTGRES,
            'sqlite': DatabaseType.SQL_LITE,
            'mock': DatabaseType.MOCK
        }
        return mappings.get(string, None)


# annotated types for usage with Mapped[]
# auto-incrementing type, useful for generating IDs
serial = typing_extensions.Annotated[
    int, 
    sqlalchemy.Sequence(start=0, increment=1, name='Sequence'), 
    sqlalchemy.orm.mapped_column(sqlalchemy.BIGINT, primary_key=True)
]

# longest 8 byte signed integer
long_int = typing_extensions.Annotated[
    int, 
    sqlalchemy.orm.mapped_column(sqlalchemy.BIGINT, nullable=False)
]

# 2 byte int
small_int = typing_extensions.Annotated[
    int,
    sqlalchemy.orm.mapped_column(sqlalchemy.SMALLINT, nullable=False)
]

# 4 byte int
mid_int = typing_extensions.Annotated[
    int,
    sqlalchemy.orm.mapped_column(sqlalchemy.INTEGER, nullable=False)
]

# fixed string types
fixed_strings = dict([
    (size, typing_extensions.Annotated[str, sqlalchemy.orm.mapped_column(sqlalchemy.CHAR(size), nullable=False)])
    for size in [16, 32, 64, 128, 256]
])

# string types
variable_strings = dict([
    (size, typing_extensions.Annotated[str, sqlalchemy.orm.mapped_column(sqlalchemy.VARCHAR(size), nullable=False)])
    for size in [16, 32, 64, 128, 256]
])

# 15 digits precision floating point number
c_double = typing_extensions.Annotated[
    float, 
    sqlalchemy.orm.mapped_column(sqlalchemy.DOUBLE, nullable=False)
]

# 7 digits precision floating point number
c_float = typing_extensions.Annotated[
    float, 
    sqlalchemy.orm.mapped_column(sqlalchemy.FLOAT, nullable=False)
]

# date + time date - (6.5.2004) time - 20:18, datetime - 6.5.2004 20:18:20
c_datetime = typing_extensions.Annotated[
    datetime.datetime,
    sqlalchemy.orm.mapped_column(sqlalchemy.TIMESTAMP, nullable=False, default=sqlalchemy.func.current_timestamp())
]

# date (6.5.2004)
c_date = typing_extensions.Annotated[
    datetime.date,
    sqlalchemy.orm.mapped_column(sqlalchemy.DATE, nullable=False)
]
    

class ModelBase(sqlalchemy.orm.DeclarativeBase):
    pass


# Database facade
class Database:


    def __init__(self, type: DatabaseType, app: Flask) -> None:
        self.engine = self._match_database_type(type, app)


    def impl(self) -> Union[SQLAlchemy]:
        return self.engine


    def _handle_sql_alchemy_setup(self, app: Flask, url: sqlalchemy.URL) -> SQLAlchemy:
        env.assign_new(url, 'SQLALCHEMY_DATABASE_URI')
        app.config.update(env.make_flask_config(env.env_flask_vars))
        handle = SQLAlchemy(
            model_class=ModelBase,
            engine_options={
                'client_encoding': 'utf8'
            }
        )
        handle.init_app(app)
        try:
            with app.app_context():
                handle.create_all()
        except:
            ...
        return handle


    def _handle_postgres_setup(self, app: Flask) -> SQLAlchemy:
        url = sqlalchemy.URL.create(
                'postgresql',
                username=env.get_var('POSTGRES_USER'),
                password=urllib.parse.quote_plus(env.get_var('POSTGRES_PASSWORD')),
                host=env.get_var('SERVER_POSTGRES_HOSTNAME'),
                port=env.get_var('SERVER_POSTGRES_PORT'),
                database=env.get_var('POSTGRES_DATABASE')
        )
        return self._handle_sql_alchemy_setup(app, url)


    def _handle_sqlite_setup(self, app: Flask) -> SQLAlchemy:
        url = sqlalchemy.URL.create(
            'sqlite',
            database=env.get_var('SQLITE_DATABASE_NAME')
        )
        return self._handle_sql_alchemy_setup(app, url)

            
    def _match_database_type(self, type: DatabaseType, app: Flask) -> Union[SQLAlchemy, None]:
        if type == DatabaseType.POSTGRES:
            return self._handle_postgres_setup(app)
        elif type == DatabaseType.SQL_LITE:
            return self._handle_sqlite_setup(app)
        elif type == DatabaseType.MOCK:
            return None
        raise ValueError(f'unimplemented: {type}')
 


            



