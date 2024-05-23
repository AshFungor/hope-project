# required library
import datetime
import logging

import pandas as pd
import app.models as models

from app.env import env
from app.modules.database.validators import CurrentTimezone


class StaticTablesHandler:

    @staticmethod
    def prepare_bank_account():
        bank_account = models.BankAccount()
        env.db.impl().session.add(bank_account)
        return bank_account.id

    @staticmethod
    def prepare_prefectures(prefectures: pd.DataFrame) -> int:
        count = 0
        try:
            for index, prefecture in prefectures.iterrows():
                prefecture_model = models.Prefecture()
                prefecture_model.bank_account_id = StaticTablesHandler.prepare_bank_account()
                prefecture_model.name = prefecture['Name']
                env.db.impl().session.add(prefecture_model)
                count += 1
            logging.debug(f'receiving new prefectures objects: {len(prefectures)} added')
        except ValueError as value_error:
            logging.warn(f'error parsing prefectures: {value_error}')
        except Exception as unknown_error:
            logging.warn(f'unknown error: {value_error}')
        finally:
            return count

    @staticmethod
    def prepare_cities(cities: pd.DataFrame) -> None:
        count = 0
        try:
            for index, city in cities.iterrows():
                city_model = models.City()
                city_model.name = city['Name']
                query = env.db.impl().session.query(models.Prefecture).filter(
                    models.Prefecture.name == city['Prefecture']).first()
                city_model.prefecture_id = query.id
                city_model.bank_account_id = StaticTablesHandler.prepare_bank_account()
                city_model.location = int(city['Location'])
                env.db.impl().session.add(city_model)
            logging.debug(f'receiving new cities objects: {len(cities)} added')
        except ValueError as value_error:
            logging.warn(f'error parsing cities: {value_error}')
        except Exception as unknown_error:
            logging.warn(f'unknown error: {value_error}')
        finally:
            return count

    @staticmethod
    def prepare_users(users: pd.DataFrame) -> None:
        count = 0
        try:
            for index, user in users.iterrows():
                birthday = datetime.date(map(int, user['Birthday'].split('.')), tzinfo=CurrentTimezone)
                user_model = models.User(
                    StaticTablesHandler.create_bank_account(),
                    env.db.impl().session.query(models.City).filter(
                        models.City.name == user['City']).first().id,
                    user['Name'],
                    user['Surname'],
                    user['Login'],
                    user['Password'],
                    user['Sex'],
                    0,
                    birthday
                )
                env.db.impl().session.add(user_model)
            logging.debug(f'receiving new user objects: {len(user)} added')
        except ValueError as value_error:
            logging.warn(f'error parsing users: {value_error}')
        except Exception as unknown_error:
            logging.warn(f'unknown error: {value_error}')
        finally:
            return count

    @staticmethod
    def prepare_products_to_bank_account(
        bank_account_id: int,
        product_id: int,
        count: int
    ) -> None:
        product_to_bank_account = models.Product2BankAccount()
        product_to_bank_account.bank_account_id = bank_account_id
        product_to_bank_account.product_id = product_id
        product_to_bank_account.count = count
        env.db.impl().session.add(product_to_bank_account)

    @staticmethod
    def prepare_product(
        category: str, 
        name: str, 
        level: int
    ) -> int:
        product = models.Product()
        product.category = category
        product.name = name
        product.level = level

        env.db.impl().session.add(product)
        return product.id
