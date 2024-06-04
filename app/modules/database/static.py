# required library
import datetime
import logging
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
            for index, prefecture in prefectures.iterrows():
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
            for index, city in cities.iterrows():
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
            for index, user in users.iterrows():
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
    def complete_transaction(transaction_id: int, with_status: str) -> (bool, str):
        completed = False
        message = ''
        transaction = env.db.impl().session.get(models.Transaction, transaction_id)
        if transaction:
            if transaction.status != 'created':
                message = 'Данное предложение уже неактивно'
                return completed, message
            if with_status == 'approved':

                # - money from customer
                customer_wallet_products = env.db.impl().session.query(models.Product2BankAccount).filter(and_(
                    or_(
                        models.Product2BankAccount.product_id == 1,  # or money's id
                        models.Product2BankAccount.product_id == transaction.product_id
                    ),
                    models.Product2BankAccount.bank_account_id == transaction.customer_bank_account_id
                ))
                customer_wallet_products[0].count -= transaction.amount

                # - product from seller
                seller_wallet_products = env.db.impl().session.query(models.Product2BankAccount).filter(and_(
                    or_(
                        models.Product2BankAccount.product_id == transaction.product_id,
                        models.Product2BankAccount.product_id == 1
                    ),
                    models.Product2BankAccount.bank_account_id == transaction.seller_bank_account_id
                ))
                seller_wallet_products[1].count -= transaction.count

                # check customer wallet and seller products
                if customer_wallet_products[0].count < 0 or seller_wallet_products[1].count < 0:
                    logging.warning('transaction was not accepted')
                    message = 'Ошибка транзакции. Либо у вас недостаточно денег на счету, либо у продовца кончился товар'
                    # rollback
                    env.db.impl().session.expire(customer_wallet_products[0])
                    env.db.impl().session.expire(seller_wallet_products[1])
                    return completed, message

                # + product to customer
                if customer_wallet_products[1]:
                    customer_wallet_products[1].count += transaction.count
                # if customer does not have products table
                else:
                    customer_products = models.Product2BankAccount()
                    customer_products.bank_account_id = transaction.customer_bank_account_id
                    customer_products.product_id = transaction.product_id
                    customer_products.count = transaction.count
                    env.db.impl().session.add(customer_products)

                # + money to seller
                seller_wallet_products[0].count += transaction.amount
                transaction.status = with_status
                transaction.updated_at = datetime.datetime.now(tz=CurrentTimezone)
                completed = True
                message = 'Предложение успешно приято'

            elif with_status == 'rejected':
                completed = True
                message = 'Предложение успешно отклонено'
                transaction.status = with_status
            else:
                message = 'Мы не нашли данное предложение'
                logging.warning('unknown transaction status')
        else:
            message = 'Ма не нашли данное предложение'
            logging.warning('transaction not found')
        return completed, message

