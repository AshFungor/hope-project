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
from abc import abstractmethod
from typing import Union

import datetime
import urllib.parse
import logging
import enum

# Session handle represents endpoint for mock session calls
# add, remove, execute, etc.
class ISessionHandle:

    # handle request from session
    @abstractmethod
    def handle_transaction(**args: dict[str, str]) -> int:
        pass


# Mock storage is used to fill absence of real
# database connection, all calls to its API are logged
# and provide data as set
class MockStorage(ISessionHandle):

    class MockSession:

        def __init__(self, handle: ISessionHandle) -> None:
            self.objects = []
            self.handle = handle
        
        def add(self, instance: object, _warn: bool = True) -> None:
            logging.debug(f'adding object: {repr(object)}')
            self.objects.append(object)

        def expunge(self, instance: object) -> None:
            logging.debug(f'removing objectL {repr(object)}')
            self.objects.remove(object)

        def commit(self) -> None:
            payload = self._make_payload()
            logging.debug(f'committing transaction with payload: {payload}')
            self.handle.handle_transaction()

        def _make_payload(self):
            payload = {}
            for i in range(len(self.objects)):
                payload[str(i)] = repr(self.objects[i])

    def handle_transaction(**args: dict[str, str]) -> int:
        logging.debug('received transaction')

    @staticmethod
    def _get_needed(config: Flask.config_class) -> dict[str, str]:
        # these are usually handled by init() from Alchemy,
        # we just parse them and ensure they are valid 
        needed_args = [
            'SQLALCHEMY_DATABASE_URI', 
            'SQLALCHEMY_ENGINE_OPTIONS',
            'SQLALCHEMY_ECHO',
            'SQLALCHEMY_BINDS',
            'SQLALCHEMY_RECORD_QUERIES',
            'SQLALCHEMY_TRACK_MODIFICATIONS'
        ]

        args = {}
        for key, value in config:
            if key in needed_args:
                args[key] = value

        for key in needed_args:
            if key not in args:
                args[key] = None
        
        msg = ';'.join(map(lambda k, v: f'arg: {k}, value: {v}',args))
        logging.debug(f'database impl is inited with args: {msg}')
        return args
    
    def __init__(self, app: Flask) -> None:
        self.args = MockStorage._get_needed(app.config)
        self.session = self._make_mock_session()

    def _make_mock_session(self) -> MockSession:
        return MockStorage.MockSession()
    
    def __repr__(self):
        return '<InPlaceStorage class>'


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

# date + time
c_datetime = typing_extensions.Annotated[
    datetime.datetime,
    sqlalchemy.orm.mapped_column(sqlalchemy.TIMESTAMP, nullable=False, default=sqlalchemy.func.current_timestamp())
]

# date
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


    def impl(self) -> Union[SQLAlchemy, MockStorage]:
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
        with app.app_context():
            handle.create_all()
        return handle


    def _handle_in_place_storage_setup(self, app: Flask) -> None:
        pass


    def _handle_postgres_setup(self, app: Flask) -> SQLAlchemy:
        url = sqlalchemy.URL.create(
                'postgresql',
                username=env.get_var('POSTGRES_USER'),
                password=urllib.parse.quote_plus(env.get_var('POSTGRES_PASSWORD')),
                host=env.get_var('POSTGRESQL_HOSTNAME'),
                port=env.get_var('POSTGRESQL_PORT'),
                database=env.get_var('POSTGRES_USER')
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
        raise ValueError(f'unimplemented: {type}')
 


            



