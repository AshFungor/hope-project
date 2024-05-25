
import unittest
import pandas
import os

from unittest.mock import patch
from unittest.mock import MagicMock
from unittest.mock import Mock

import mock_storage

# set vars for global config
os.environ['SERVER_LOGGING_STORAGE_TYPE'] = 'local'
os.environ['SERVER_LOGGING_LOCATION'] = './'

import app.main
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

        env.db = self.db
        self.server = server
        self.client = server.test_client()

    def tearDown(self) -> None:
        env.logging_listeners.stop()
        os.remove(env.server_logging_file)

    @staticmethod
    def make_user_payload() -> str:
        payload = pandas.DataFrame(columns=['Birthday', 'Name', 'Surname', 'Login', 'Password', 'City', 'Sex'])
        for i in range(10):
            payload.loc[i] = ['1.1.2020', 'Имя', 'Фамилия', 'login', 'lol', 'city', 'female']
        return payload.to_csv(sep=',')
    
    @staticmethod
    def make_cities_payload() -> str:
        payload = pandas.DataFrame(columns=['Name', 'Location', 'Prefecture'])
        for i in range(10):
            payload.loc[i] = ['Lol', 'Kek', 'More fields?']
        return payload.to_csv(sep=',')
    
    @staticmethod
    def make_prefectures_payload() -> str:
        payload = pandas.DataFrame(columns=['Name'])
        for i in range(10):
            payload.loc[i] = ['Lol']
        return payload.to_csv(sep=',')

    def test_requests(self) -> None:
        print(f'users: \n{CsvApiTest.make_user_payload()}')
        response = self.client.post('/upload/csv/users', data=CsvApiTest.make_user_payload())
        self.assertEqual(response.status_code, 200)
        print(f'cities: \n{CsvApiTest.make_cities_payload()}')
        response = self.client.post('/upload/csv/cities', data=CsvApiTest.make_cities_payload())
        self.assertEqual(response.status_code, 200)
        print(f'prefectures: \n{CsvApiTest.make_prefectures_payload()}')
        response = self.client.post('/upload/csv/prefectures', data=CsvApiTest.make_prefectures_payload())
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
