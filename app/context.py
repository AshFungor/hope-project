import logging
import logging.handlers
import multiprocessing
import sys
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Self, Type, Union
from zoneinfo import ZoneInfo

import colorlog
import sqlalchemy as orm
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from yaml import Loader, MappingNode, UnsafeLoader, YAMLObject, load

from app.models.types import ModelBase


@dataclass
class AppConfig(YAMLObject):

    @dataclass
    class Logging(YAMLObject):
        yaml_tag = "!logging"

        stdout: bool = True
        stderr: bool = False
        file: Optional[Path] = None
        rotation_threshold: int = 1024 * 1024 * 8  # 8 Mib
        backups: int = 2
        level: str = "debug"

    @dataclass
    class Database(YAMLObject):
        yaml_tag = "!database"

        @dataclass
        class SQLite(YAMLObject):
            yaml_tag = "!sqlite"

            database_name: str

        @dataclass
        class Postgres(YAMLObject):
            yaml_tag = "!postgres"

            directory: Path
            hostname: str
            port: int
            # should be moved into the vault
            password: str
            user: str
            database_name: str

        kind: Union[Postgres, SQLite]

        __kinds = Union[Type[Postgres], Type[SQLite]]
        __kind_objects = Union[Postgres, SQLite]

        def visit(self, f: Dict[__kinds, Callable[[__kind_objects], Any]]) -> Any:
            if isinstance(self.kind, self.SQLite):
                return f[self.SQLite](self.kind)
            if isinstance(self.kind, self.Postgres):
                return f[self.Postgres](self.kind)

            raise ValueError

    @dataclass
    class Consumption(YAMLObject):
        yaml_tag = "!consumption"

        @dataclass
        class CategoryInfo:
            count: int
            price: int
            period_days: int

        categories: Dict[str, CategoryInfo]

        @classmethod
        def from_yaml(cls, loader: Loader, node: MappingNode) -> Self:
            raw_dict = loader.construct_mapping(node, deep=True)
            return cls({category: cls.CategoryInfo(**data) for category, data in raw_dict.items()})

    @dataclass
    class FlaskExtensions(YAMLObject):
        yaml_tag = "!flask_extensions"

        csrf: bool = True
        login_manager: bool = True

    def __post_init__(self):
        self.timezone = ZoneInfo(self.timezone)

    secret: str
    timezone: ZoneInfo
    database: Database
    logging: Logging
    flask_extensions: FlaskExtensions
    consumption: Consumption


class AppContext:
    __instance: "AppContext" = None
    __format_str = "[%(asctime)s][%(name)s] %(levelname)s: %(message)s"
    __colorful_format_str = "[%(log_color)s%(asctime)s][%(name)s] %(levelname)s: %(message)s"

    def __new__(cls, *__args, **__kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, app: Flask, config_path: Path):
        if not config_path.is_file():
            raise FileNotFoundError(config_path)

        with open(config_path, "r") as fd:
            self.__config = AppConfig(**load(fd, UnsafeLoader))

        self.__app = app
        self.__app.secret_key = self.__config.secret
        self.__init_database_conn()
        self.__init_logging()

    @classmethod
    def safe_load(cls) -> Self:
        if cls.__instance is None:
            raise RuntimeError("App context was not initialized properly, something is wrong" " with how you manage runtime environment")
        return cls.__instance

    @property
    def database(self) -> SQLAlchemy:
        return self.__database_handle

    @property
    def config(self) -> AppConfig:
        return self.__config

    @property
    def logger(self) -> logging.Logger:
        return self.__logger

    @property
    def app(self) -> Flask:
        return self.__app

    def __init_database_conn(self):
        def handle_sqlite(conf: AppConfig.Database.SQLite):
            return orm.URL.create(drivername="sqlite", database=conf.database_name)

        def handle_postgres(conf: AppConfig.Database.Postgres):
            return orm.URL.create(
                "postgresql", username=conf.user, password=conf.password, host=conf.hostname, port=conf.port, database=conf.database_name
            )

        uri = self.__config.database.visit({AppConfig.Database.SQLite: handle_sqlite, AppConfig.Database.Postgres: handle_postgres})

        self.__app.config.update({"SQLALCHEMY_DATABASE_URI": uri})

        self.__database_handle = SQLAlchemy(model_class=ModelBase)
        self.__database_handle.init_app(self.__app)
        with self.__app.app_context():
            self.__database_handle.create_all()

    def __init_logging(self):
        level = self.__validate_logging_level(self.__config.logging.level)

        color_formatter = colorlog.ColoredFormatter(
            self.__colorful_format_str, log_colors={"DEBUG": "cyan", "INFO": "green", "WARNING": "yellow", "ERROR": "red", "CRITICAL": "bold_red"}
        )

        handlers: List[logging.Handler] = []
        if self.__config.logging.stdout:
            handlers.append(logging.StreamHandler(sys.stdout))
        if self.__config.logging.stderr:
            handlers.append(logging.StreamHandler(sys.stderr))

        # can be applied only to standard error/out
        for handler in handlers:
            handler.setFormatter(color_formatter)

        if self.__config.logging.file is not None:
            file_handler = logging.handlers.RotatingFileHandler(
                filename=self.__config.logging.file, maxBytes=self.__config.logging.rotation_threshold, backupCount=self.__config.logging.backups
            )
            handlers.append(file_handler)

        queue = multiprocessing.Queue()
        queue_handler = logging.handlers.QueueHandler(queue)
        self.__listeners = logging.handlers.QueueListener(queue, *handlers)
        self.__listeners.start()

        logging.basicConfig(level=level, handlers=[queue_handler], format=self.__format_str, force=True)

        self.__logger = logging.getLogger("app")
        self.__logger.info(f"Logging initialized with level: {self.__config.logging.level}")

    def __validate_logging_level(self, level: str) -> int:
        levels = {"debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING, "error": logging.ERROR, "critical": logging.CRITICAL}
        return levels.get(level.lower(), logging.DEBUG)


def class_context(f: Callable) -> Callable:
    @wraps(f)
    def wrapper(*args, **kwargs):
        # safe to call if init() is triggered already
        ctx = AppContext.safe_load()
        return f(*args, ctx=ctx, **kwargs)

    return wrapper


def function_context(f: Callable) -> Callable:
    @wraps(f)
    def wrapper(*args, **kwargs):
        ctx = AppContext.safe_load()
        return f(ctx, *args, **kwargs)

    return wrapper
