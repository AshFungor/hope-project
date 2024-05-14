# sql alchemy
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

# default
from abc import abstractmethod
from typing import Union
import logging

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


# Database facade
class Database:

    def __init__(self, engine: Union[SQLAlchemy, MockStorage]) -> None:
        self.engine = engine
        self.setup()

    def impl(self) -> Union[SQLAlchemy, MockStorage]:
        return self.engine

    def setup(self) -> int:
        if isinstance(self.engine, SQLAlchemy):
            self._handle_sql_alchemy_setup()
            return
        
        if isinstance(self.engine, MockStorage):
            self._handle_in_place_storage_setup()
            return

        raise TypeError(f'database impl is not supported: {repr(self.engine)}')

    def connect(self) -> int:
        if isinstance(self.engine, SQLAlchemy):
            pass
        
        if isinstance(self.engine, MockStorage):
            pass

    def _handle_sql_alchemy_setup(self):
        if not hasattr(self.engine, 'session'):
            raise ValueError('database sql alchemy impl must be initialized, missing session attr')

    def _handle_in_place_storage_setup(self):
        pass



