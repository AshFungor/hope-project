import app.main

import unittest
import random
import json
import os

from unittest.mock import patch
from unittest.mock import MagicMock
from unittest.mock import Mock

import mock_storage

# set vars for global config
os.environ['SERVER_LOGGING_STORAGE_TYPE'] = 'local'
os.environ['SERVER_LOGGING_LOCATION'] = './'

from app.env import env


class CsvApiTest(unittest.TestCase):

    def setUp(self) -> None:        
        self.db = Mock()
        self.storage = mock_storage.MockStorage()
        self.db.impl = MagicMock(return_value=self.storage)

        env.server_database_type = 'mock'
        server = app.main.create_app()
        server.config.update({
            "TESTING": True,
        })

        self.server = server
        self.client = server.test_client()

    def tearDown(self) -> None:
        env.logging_listeners.stop()
    
    @staticmethod
    def make_row(*args: list[str]) -> str:
        return ';'.join(args) + '\n'

    @staticmethod
    def make_user_payload() -> str:
        payload = CsvApiTest.make_row('Birthday', 'Name', 'Surname', 'Login', 'Password', 'Sex')
        for _ in range(10):
            payload += CsvApiTest.make_row('1.1.2020', 'Имя', 'Фамилия', 'Some Login', 'Some Password', 'female')
        return payload

    def test_correct_request(self) -> None:
        response = self.client.post('/upload/csv/users', json=json.dumps({
            'Users': CsvApiTest.make_user_payload()
        }))

        self.assertEqual(response.status_code, 200)



if __name__ == '__main__':
    unittest.main() 







