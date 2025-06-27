# required library
import datetime
import logging
import typing
import uuid

import sqlalchemy

import pandas as pd
import numpy as np

import app.models as models

from app.env import env
from app.modules.database.validators import CurrentTimezone


def roller(**kwargs) -> models.BankAccount:
    seed = models.BankAccount(**kwargs)
    while env.db.impl().session.query(models.BankAccount).get(seed.id) is not None:
        seed = models.BankAccount(**kwargs)
    return seed


class StaticTablesHandler:

    @staticmethod
    def prepare_bank_account(**kwargs: dict[str, object]) -> int | None:
            bank_account = roller(**kwargs)
            # to try transactions
            bind_account = models.Product2BankAccount(bank_account.id, 1, 200 if env.debug else 0)
            env.db.impl().session.add(bank_account)
            env.db.impl().session.add(bind_account)
            return bank_account.id

    @staticmethod
    def __parse_prefectures(prefectures: pd.DataFrame) -> list[models.Prefecture] | str:
        existing = np.asarray(env.db.impl().session.query(models.Prefecture.name).all(), dtype='str')
        parsed = []

        for index, prefecture in prefectures.iterrows():
            prefecture_name = prefecture.get('Name', None)
            if prefecture_name is None:
                return f'series at index {index} lacking field: Name'
            if np.any(existing == prefecture_name):
                return f'prefecture at index {index} called {prefecture_name} already existing'

            account = StaticTablesHandler.prepare_bank_account(**models.BankAccount.make_spec(
                'prefecture', prefecture
            ))
            if account is None:
                return f'error generating bank account for index {index}'

            parsed.append(models.Prefecture(
                prefecture_name,
                account,
                None,
                None,
                None
            ))

        return parsed    

    @staticmethod
    def prepare_prefectures(prefectures: pd.DataFrame) -> int | str:
        parsed = []
        try:
            parsed = StaticTablesHandler.__parse_prefectures(prefectures)
            if isinstance(parsed, str):
                return parsed
            env.db.impl().session.add_all(parsed)
            return len(parsed)
        except Exception as error:
            env.db.impl().session.rollback()
            return f'error parsing prefectures: {error}'

    @staticmethod
    def __prepare_cities(cities: pd.DataFrame) -> list[models.City] | str:
        existing = [
            np.asarray(env.db.impl().session.query(models.City.name).all()),
            np.asarray(env.db.impl().session.query(models.City.location).all()),
            np.ones(0)
        ]
        parsed = []

        for index, city in cities.iterrows():
            city_name, city_location, city_prefecture = \
                city.get('Name', None), city.get('Location', None), city.get('Prefecture', None)

            for feature, lookup, objects in zip(['name', 'location', 'prefecture'], [city_name, city_location, city_prefecture], existing):
                if lookup is None:
                    return f'series at index {index} lacking field: {feature}'
                if np.any(objects == lookup):
                    return f'attribute {feature} at index {index} already exists'

            prefecture = env.db.impl().session.query(models.Prefecture).filter(
                models.Prefecture.name == city_prefecture
            ).first()
            if prefecture is None:
                return f'failed to find prefecture with name {city_prefecture}'
            prefecture_id = prefecture.id
            
            bank_account = StaticTablesHandler.prepare_bank_account(**models.BankAccount.make_spec(
                'city', city
            ))
            if bank_account is None:
                return f'error generating bank account for index {index}'

            parsed.append(models.City(
                city_name,
                None,
                prefecture_id,
                bank_account,
                city_location
            ))

        return parsed

    @staticmethod
    def prepare_cities(cities: pd.DataFrame) -> int | str:
        parsed = []
        try:
            parsed = StaticTablesHandler.__prepare_cities(cities)
            if isinstance(parsed, str):
                return parsed
            env.db.impl().session.add_all(parsed)
            return len(parsed)
        except Exception as error:
            env.db.impl().session.rollback()
            return f'error parsing cities: {error}'

    @staticmethod
    def __prepare_users(users: pd.DataFrame) -> int | str:
        existing = [
            np.ones(0),
            np.ones(0),
            np.ones(0),
            np.asarray(env.db.impl().session.query(models.User.login).all()),
            np.ones(0), # filler for password
            np.ones(0), # filler for sex
            np.ones(0), # filler for birthday
            np.ones(0), # filler for admin
        ]
        parsed = []

        for index, user in users.iterrows():
            user_name, user_surname, user_patronymic, user_login, user_password, user_sex, user_birthday, user_bonus, user_admin =   \
                user.get('Name', None), user.get('Surname', None), user.get('Patronymic', None), user.get('Login', None),                       \
                user.get('Password', None), user.get('Sex', None), user.get('Birthday', None),                          \
                user.get('Bonus', None), user.get('IsAdmin', None)

            # fuck, this gets to me...
            for feature, lookup, objects in zip(
                ['name', 'surname', 'patronymic', 'login', 'password', 'sex', 'birthday', 'bonus', 'is_admin'], 
                [user_name, user_surname, user_patronymic, user_login, user_password, user_sex, user_birthday, user_bonus, user_admin], 
                existing
            ):
                if lookup is None:
                    return f'series at index {index} lacking field: {feature}'
                if np.any(objects == lookup):
                    return f'attribute {feature} at index {index} already exists'
                
            user_birthday = datetime.date(*reversed(list(map(int, user_birthday.split('.')))))

            # user_city_obj = env.db.impl().session.query(models.City.id).filter(
            #     models.City.name == user_city
            # ).first()
            # if user_city_obj is None:
            #     return f'failed to find city with name {user_city}'
            # user_city_id = user_city_obj.id
            
            bank_account = StaticTablesHandler.prepare_bank_account(**models.BankAccount.make_spec(
                'user', user
            ))
            if bank_account is None:
                return f'error generating bank account for index {index}'

            parsed.append(models.User(
                bank_account,
                # user_city_id,
                None,
                user_name.strip(),
                user_surname.strip(),
                user_patronymic.strip(),
                user_login.strip(),
                user_password.strip(),
                user_sex,
                int(user_bonus),
                user_birthday,
                user_admin == 'true'
            ))

        return parsed

    @staticmethod
    def prepare_users(users: pd.DataFrame) -> int | str:
        parsed = []
        parsed = StaticTablesHandler.__prepare_users(users)
        if isinstance(parsed, str):
            return parsed
        env.db.impl().session.add_all(parsed)
        return len(parsed)


    @staticmethod
    def prepare_products_to_bank_account(
        bank_account_id: int,
        product_id: int,
        count: int
    ) -> None:
        product_to_bank_account = models.Product2BankAccount(
            bank_account_id,
            product_id,
            count
        )
        env.db.impl().session.add(product_to_bank_account)

    @staticmethod
    def __prepare_products(products: pd.DataFrame) -> int | str:
        existing = [
            np.asarray(env.db.impl().session.query(models.Product.name).all(), dtype='str'),
            np.ones(0),
            np.ones(0)
        ]
        parsed = []

        for index, product in products.iterrows():
            product_name, product_category, product_level = \
                product.get('Name', None), product.get('Category', None), product.get('Level', None)
            for feature, lookup, objects in zip(['name', 'category', 'level'], [product_name, product_category, product_level], existing):
                if lookup is None:
                    return f'series at index {index} lacking field: {feature}'
                if np.any(objects == lookup):
                    return f'attribute {feature} at index {index} already exists'

            parsed.append(models.Product(
                product_category,
                product_name,
                int(product_level)
            ))

        return parsed

    @staticmethod
    def prepare_products(products: pd.DataFrame) -> int:
        parsed = []
        try:
            parsed = StaticTablesHandler.__prepare_products(products)
            if isinstance(parsed, str):
                return parsed
            env.db.impl().session.add_all(parsed)
            return len(parsed)
        except Exception as error:
            env.db.impl().session.rollback()
            return f'error parsing products: {error}'

    @staticmethod
    def complete_transaction(transaction_id: int, with_status: str) -> typing.Tuple[str, bool]:
        transaction = env.db.impl().session.get(models.Transaction, transaction_id)
        if not transaction:
            return 'could not find transaction', False

        message, status = transaction.process(with_status == 'approved')
        if not status:
            env.db.impl().session.rollback()
            logging.warning(f'transaction {transaction_id}; error {message}')

        env.db.impl().session.commit()
        return message, status


