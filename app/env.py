# default
import os
import sys
import logging
import os.path
import logging.handlers
import multiprocessing

from typing import Union

# dotenv package
import dotenv

# flask stuff
import flask


class Env:

    env_value_placeholder = None
    # PLEASE ADD NEW VARS TO THE END AND DO NOT REMOVE THESE!!!
    env_vars = [
        'SERVER_DATABASE_TYPE', 
        'SERVER_LOGGING_LEVEL',
        'FLASK_ENV',
        'FLASK_DEBUG',
        'SERVER_LOGGING_STORAGE_TYPE',
        'SERVER_LOGGING_LOCATION',
        'POSTGRES_USER',
        'POSTGRES_PASSWORD',
        'POSTGRES_DATABASE',
        'SERVER_POSTGRES_HOSTNAME',
        'SERVER_POSTGRES_PORT',
        'SQLITE_DATABASE_NAME',
        'DEBUG',
    ]
    env_flask_vars = [
        'SQLALCHEMY_DATABASE_URI'
    ]
    env_defaults = {
        'SERVER_DATABASE_TYPE': 'sqlite',
        'SERVER_LOGGING_LEVEL': 'debug',
        'FLASK_ENV': 'development',
        'FLASK_DEBUG': True,
        'SERVER_LOGGING_STORAGE_TYPE': 'local',
        'SERVER_LOGGING_LOCATION': './log/'
    }
    env_logging_levels = {
        'debug': logging.DEBUG, 
        'info': logging.INFO, 
        'warning': logging.WARNING, 
        'error': logging.ERROR, 
        'critical': logging.CRITICAL
    }
    env_logging_storages = [
        'system',
        'local'
    ]
    # add some json config later


    def __init__(self) -> None:
        # load env args
        debugStr = self._load_env_from_file()

        for var in Env.env_vars:
            value = os.environ.get(var, None)
            # if env variable does not exist...
            if value is None:
                if var in Env.env_defaults:
                    # if we have default, set it
                    value = Env.env_defaults[var]
                    debugStr += f'env: var {var} was not fetched, setting it to default: {value}; '
                elif hasattr(self, var.lower()):
                    value = getattr(self, var.lower())
                else:
                    # else just put None
                    value = Env.env_value_placeholder
                    debugStr += f'env: var {var} was not fetched, setting it to {value}; '
            else: 
                # success, we fetched var and assigned to our global things storage (Env)
                debugStr += f'env: var {var} fetched, setting it to {value}; '
            setattr(self, var.lower(), value)
        
        self.loaded = True
        self._init_logging()

        # log first message!
        logging.info(debugStr)
        logging.info('initialized environment singleton')
    

    def make_flask_config(self, fields: list[str], only_env: bool = True) -> flask.Config:
        config = flask.Config('.env')
        for field in fields:
            if hasattr(self, field.lower()) and (not only_env or True): # for now
                config[field.upper()] = getattr(self, field.lower())
            else:
                logging.warning(f'missing requested field: {field}')
                config[field.upper()] = None
        return config
    
    
    # check if set logging level is a valid string 
    def _validate_logging_level(self, level: str) -> int: # just an int constant actually
        if level not in Env.env_logging_levels:
            return logging.DEBUG
        return Env.env_logging_levels[level]
    

    # match logging file locations
    def _match_logging_location(self, logging_storage_type: str) -> str:
        if logging_storage_type in Env.env_logging_storages:
            if logging_storage_type == 'system':
                # fetch path to system log
                return self.server_logging_location
            elif logging_storage_type == 'local':
                return './'

    
    def _init_logging(self) -> None:
        # check if configs were parsed and valid
        if not hasattr(self, 'loaded') or not self.loaded:
            raise ValueError('Environment must be initialized before logging')
        # loggers are essentially endpoints that receive logged() messages
        # and route them in whatever way (to file, to standard output or error streams - terminal)
        self.server_logging_file = self._match_logging_location(
            self.server_logging_storage_type) + f'server-{os.getpid()}.log'
        file_log_sink = logging.handlers.RotatingFileHandler(
            self.server_logging_file, 
            maxBytes=4096, 
            backupCount=2
        )
        std_out_sink = logging.StreamHandler(sys.stdout)
        # std_err_sink = logging.StreamHandler(sys.stderr)
        # we also need to sync file rotation, because it dies on windows
        queue = multiprocessing.Queue()
        queue_handler = logging.handlers.QueueHandler(queue)
        listeners = logging.handlers.QueueListener(queue, file_log_sink, std_out_sink)
        # logging is by default done only for warnings and errors
        # for sanity, we enable for debug additionally
        logging.basicConfig(
            handlers=[
                queue_handler
            ],
            level=self._validate_logging_level(getattr(self, 'server_logging_level')),
            force=True # in case logger was already configured for some reason
        )

        self.logging_listeners = listeners
        self.logging_listeners.start()


    # load env from file
    def _load_env_from_file(self, filename: Union[str, None] = '.env') -> str:
        debugString = ''
        if os.path.exists(filename) and os.path.isfile(filename):
            dotenv.load_dotenv(dotenv_path=filename, override=False)
            debugString += 'loaded env vars from .env file; '
        else:
            debugString += 'did not found .env file; '
        return debugString


    # sets new global, also performs some simple checks
    def assign_new(self, object: object, field_name: str) -> None:
        if hasattr(self, field_name.lower()):
            raise ValueError(f'global scope already has this variable: {field_name.lower()}')
        # maybe more checks?
        setattr(self, field_name.lower(), object)

    # gets value from current env, essentially patched getattr
    def get_var(self, name: str) -> object:
        if not hasattr(self, name.lower()):
            raise ValueError(f'requested {name.upper()} variable is not present in env')
        return getattr(self, name.lower())


# create singleton to hold all global data
env = Env()
            