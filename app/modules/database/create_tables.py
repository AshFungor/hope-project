import os, csv
from app.env import env
import app.models as models
import datetime
from app.modules.database.validators import CurrentTimezone


class TablesCreator:

    def __init__(self):
        self._created_start_tables_check = False

    @property
    def created_tables(self):
        return self._created_start_tables_check

    @created_tables.getter
    def check(self):
        return self._created_start_tables_check

    def create_bank_account(self):
        bank_account = models.BankAccount()
        env.db.impl().session.add(bank_account)
        env.db.impl().session.commit()
        return bank_account.id

    def create_prefectures(self):
        with open(os.path.join(os.getcwd(), 'app/static/csv/Prefectures.csv'), encoding='utf-8-sig') as csv_prefectures:
            prefectures = csv.DictReader(csv_prefectures, delimiter=';')
            for prefecture in prefectures:
                prefecture_model = models.Prefecture()
                prefecture_model.bank_account_id = self.create_bank_account()
                prefecture_model.name = prefecture['Название префектуры'].capitalize()
                env.db.impl().session.add(prefecture_model)
        env.db.impl().session.commit()

    def create_cities(self):
        with open(os.path.join(os.getcwd(), 'app/static/csv/Cities.csv'), encoding='utf-8-sig') as csv_cities:
            cities = csv.DictReader(csv_cities, delimiter=';')
            for city in cities:
                city_model = models.City()
                city_model.name = city['Название города'].capitalize()
                query = env.db.impl().session.query(models.Prefecture).filter(
                    models.Prefecture.name == city['Префектура города'].capitalize()).first()
                city_model.prefecture_id = query.id
                city_model.bank_account_id = self.create_bank_account()
                city_model.location = int(city['Комната'])
                env.db.impl().session.add(city_model)
        env.db.impl().session.commit()

    def create_users(self):
        with open(os.path.join(os.getcwd(), 'app/static/csv/Users.csv'), encoding='utf-8-sig') as csv_users:
            users = csv.DictReader(csv_users, delimiter=';')
            for user in users:
                list_date_birthday = list(map(int, user['Дата рождения'].split('.')))
                birthday = datetime.datetime(
                    year=list_date_birthday[-1],
                    month=list_date_birthday[-2],
                    day=list_date_birthday[-3],
                    tzinfo=CurrentTimezone
                )
                user_model = models.User(
                    self.create_bank_account(),
                    env.db.impl().session.query(models.City).filter(
                        models.City.name == user['Город']).first().id,
                    user['Имя'].capitalize(),
                    user['Фамилия'].capitalize(),
                    user['Логин'],
                    user['Пароль'],
                    'male' if user['Пол'].lower() == 'мужской' else 'female',
                    0,
                    birthday
                )
                env.db.impl().session.add(user_model)
                self.create_start_kit(user_model.bank_account_id)

        env.db.impl().session.commit()

    def create_start_kit(self, bank_account_id: int):

        # add money
        self.create_products_to_bank_account(
            bank_account_id,
            1,
            1000
        )

        # add eat
        self.create_products_to_bank_account(
            bank_account_id,
            product_id=2,
            count=20
        )

        # add clothes
        self.create_products_to_bank_account(
            bank_account_id,
            product_id=3,
            count=10
        )

        # add gadgets
        self.create_products_to_bank_account(
            bank_account_id,
            product_id=4,
            count=5
        )

    def create_products_to_bank_account(
            self,
            bank_account_id: int,
            product_id: int,
            count: int
    ):
        product_to_bank_account = models.Product2BankAccount()
        product_to_bank_account.bank_account_id = bank_account_id
        product_to_bank_account.product_id = product_id
        product_to_bank_account.count = count
        env.db.impl().session.add(product_to_bank_account)
        env.db.impl().session.commit()

    def create_start_products(self):

        # money
        self.create_product(
            'деньги',
            'надики',
            0,
        )

        # eat
        self.create_product(
            'еда',
            'яблоки',
            0,
        )

        # clothes
        self.create_product(
            'одежда',
            'спротивный костюм',
            0,
        )

        # gadgets
        self.create_product(
            'электроника',
            'кнопочный телефон',
            0,
        )

    def create_product(self, category: str, name: str, level: int):
        product = models.Product()
        product.category = category
        product.name = name
        product.level = level

        env.db.impl().session.add(product)
        env.db.impl().session.commit()
        return product.id

    def create_all_start_tables(self):
        if not self._created_start_tables_check:
            self.create_prefectures()
            self.create_cities()
            self.create_start_products()
            self.create_users()
            self._created_start_tables_check = True


TbCreator = TablesCreator()
