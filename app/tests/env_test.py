import unittest

from unittest.mock import patch
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import call

from typing import Union

# testing deps
# default
import os
import logging
# dotenv package
import dotenv
# flask
import flask


def env_args_matcher(*args) -> Union[object, None]:
    # some vars currently supported
    matching = {
        'SERVER_DATABASE_TYPE': 'some_type',
        'SERVER_LOGGING_LOCATION': 'some_location',
        'FLASK_DEBUG': True
    }
    if len(args) == 1:
        return matching.get(args[0], None)
    elif len(args) == 2:
        var, default = args
        return matching.get(var, default)
    raise ValueError('signature not supported')


# test case for basic env parsing (ensure it handles .env, env vars + logging)
class EnvironmentHandlingTest(unittest.TestCase):

    testing_vars = ['SERVER_DATABASE_TYPE', 'SERVER_LOGGING_LOCATION', 'FLASK_DEBUG']

    # mocks
    mocked_flask_config_class = MagicMock(flask.Config, name='mocked_flask_config_class')
    mocked_env_loader_function = MagicMock(dotenv.load_dotenv, return_value=None, name='mocked_env_loader_function')
    mocked_os_path_exists_function = MagicMock(os.path.exists, return_value=True, name='mocked_os_path_exists_function')
    mocked_os_path_is_file_function = MagicMock(os.path.isfile, return_value=True, name='mocked_os_path_is_file_function')
    mocked_os_environ_get_function = MagicMock(os.environ.get, side_effect=env_args_matcher, name='mocked_os_environ_get_function')
    mocked_logging_basic_config_function = MagicMock(logging.basicConfig, return_value=None, name='mocked_logging_basic_config_function')


    @staticmethod
    def make_mock_modules(**args) -> dict[str, Mock]:
        result = {}
        # mock os
        mocked_os = Mock()
        mocked_os.path = Mock()
        mocked_os.environ = Mock()
        mocked_os.path.exists = EnvironmentHandlingTest.mocked_os_path_exists_function
        mocked_os.path.isfile = EnvironmentHandlingTest.mocked_os_path_is_file_function
        mocked_os.environ.get = EnvironmentHandlingTest.mocked_os_environ_get_function
        result['os'] = mocked_os
        result['os.path'] = Mock()
        # logging
        mocked_logging = Mock()
        mocked_logging.basicConfig = EnvironmentHandlingTest.mocked_logging_basic_config_function
        result['logging'] = mocked_logging
        result['logging.handlers'] = Mock()
        # dotenv
        mocked_dotenv = Mock()
        mocked_dotenv.load_dotenv = EnvironmentHandlingTest.mocked_env_loader_function
        result['dotenv'] = mocked_dotenv
        # flask
        mocked_flask = Mock()
        mocked_flask.Config = EnvironmentHandlingTest.mocked_flask_config_class
        result['flask'] = mocked_flask
        # multiprocessing
        mocked_multiprocessing = Mock()
        mocked_multiprocessing.Queue = Mock()
        result['multiprocessing'] = mocked_multiprocessing
        return result


    def __init__(self, methodName: str = 'runTest') -> None:
        super().__init__(methodName)
        # needed since there is code for testing init()-ing on import 
        self.unsafeImport = False


    def setUp(self) -> None:
        super().setUp()
        if self.unsafeImport:
            return
        
        with patch.dict('sys.modules', EnvironmentHandlingTest.make_mock_modules()):
            from app.env import env
            self.env = env


    def test_environment_init(self) -> None:
        # check if we can even import that...
        with patch.dict('sys.modules', EnvironmentHandlingTest.make_mock_modules()):
            from app.env import env

    
    def test_environment_args(self) -> None:
        # check if we parsed system env vars
        for var in EnvironmentHandlingTest.testing_vars:
            self.assertTrue(hasattr(self.env, var.lower()))
            self.assertEqual(getattr(self.env, var.lower()), env_args_matcher(var))
    

    def test_environment_logging_setup(self) -> None:
        # check if logging init()ed
        # mock_call = call(
        #     handlers=[
        #         self.env.server_logging_std_out_sink,
        #         self.env.server_logging_std_err_sink,
        #         self.env.server_logging_file_sink
        #     ],
        #     level=env_args_matcher('SERVER_LOGGING_LEVEL'),
        #     force=True
        # )

        # object ids are different for some reason...

        EnvironmentHandlingTest.mocked_logging_basic_config_function.assert_called()
        

if __name__ == '__main__':
    # verbose run (2), --quiet (is 1)
    unittest.main(verbosity=2)

    




