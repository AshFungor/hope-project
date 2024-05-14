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
        'SQLALCHEMY_DATABASE_URI', 
        'SERVER_USE_MOCKED_DATABASE',
        'SERVER_LOGGING_LEVEL',
        'FLASK_ENV',
        'FLASK_DEBUG'
    ]
    env_flask_vars = [
        'SQLALCHEMY_DATABASE_URI'
    ]
    env_defaults = {
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///DataBase.db',
        'SERVER_USE_MOCKED_DATABASE': False,
        'SERVER_LOGGING_LEVEL': 'debug',
        'FLASK_ENV': 'development',
        'FLASK_DEBUG': True
    }
    env_logging_levels = {
        'debug': logging.DEBUG, 
        'info': logging.INFO, 
        'warning': logging.WARNING, 
        'error': logging.ERROR, 
        'critical': logging.CRITICAL
    }
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
        
    
    def _init_logging(self) -> None:
        # check if configs were parsed and valid
        if not hasattr(self, 'loaded') or not self.loaded:
            raise ValueError('Environment must be initialized before logging')
        # loggers are essentially endpoints that receive logged() messages
        # and route them in whatever way (to file, to standard output or error streams - terminal)
        file_log_sink = logging.handlers.RotatingFileHandler('server.log', maxBytes=4096, backupCount=2)
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
        if hasattr(self, field_name):
            raise ValueError('global scope already has this variable')
        # maybe more checks?
        setattr(self, field_name, object)


# create singleton to hold all global data
env = Env()
            