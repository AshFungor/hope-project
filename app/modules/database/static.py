# required library
import datetime
import logging
import typing
import uuid

import pandas as pd
import app.models as models

from app.env import env
from app.modules.database.validators import CurrentTimezone

from sqlalchemy import and_, or_


class StaticTablesHandler:

    @staticmethod
    def prepare_bank_account(**kwargs: dict[str, object]) -> int:
        bank_account = models.BankAccount(**kwargs)
        env.db.impl().session.add(bank_account)
        return bank_account.id

    @staticmethod
    def prepare_prefectures(prefectures: pd.DataFrame) -> int:
        count = 0
        try:
            for _, prefecture in prefectures.iterrows():
                prefecture_model = models.Prefecture(
                    prefecture['Name'],
                    StaticTablesHandler.prepare_bank_account(**models.BankAccount.make_spec(
                        'prefecture', prefecture
                    )),
                    None,
                    None,
                    None
                )
                env.db.impl().session.add(prefecture_model)
                count += 1
            logging.debug(f'receiving new prefectures objects: {count} added')
        except ValueError as value_error:
            logging.warn(f'error parsing prefectures: {value_error}')
        except Exception as unknown_error:
            logging.warn(f'unknown error: {unknown_error}')
        finally:
            return count

    @staticmethod
    def prepare_cities(cities: pd.DataFrame) -> None:
        count = 0
        try:
            for _, city in cities.iterrows():
                city_model = models.City(
                    city['Name'],
                    None,
                    env.db.impl().session.query(models.Prefecture).filter(
                        models.Prefecture.name == city['Prefecture']).first().id,
                    StaticTablesHandler.prepare_bank_account(**models.BankAccount.make_spec(
                        'city', city
                    )),
                    city['Location']
                )
                env.db.impl().session.add(city_model)
                count += 1
            logging.debug(f'receiving new cities objects: {count} added')
        except ValueError as value_error:
            logging.warning(f'error parsing cities: {value_error}')
        except Exception as unknown_error:
            logging.warning(f'unknown error: {unknown_error}')
        finally:
            return count

    @staticmethod
    def prepare_users(users: pd.DataFrame) -> None:
        count = 0
        try:
            for _, user in users.iterrows():
                birthday = datetime.date(*reversed(list(map(int, user['Birthday'].split('.')))))
                user_model = models.User(
                    StaticTablesHandler.prepare_bank_account(**models.BankAccount.make_spec(
                        'user', user
                    )),
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
                count += 1
            logging.debug(f'receiving new user objects: {count} added')
        except ValueError as value_error:
            logging.warning(f'error parsing users: {value_error}')
        except Exception as unknown_error:
            logging.warning(f'unknown error: {unknown_error}')
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

    @staticmethod
    def complete_transaction(transaction_id: int, with_status: str) -> typing.Tuple[str, bool]:
        transaction = env.db.impl().session.get(models.Transaction, transaction_id)
        if not transaction:
            return 'could not find transaction', False
        
        message, status = transaction.process(with_status == 'approved')
        if not status:
            logging.warning(f'transaction {transaction_id}; error {message}')

        return message, status


