import datetime

from flask import Blueprint, render_template, url_for

from app.env import env
from app import models
from app.modules.database.static import CurrentTimezone
from app.modules.database.static import StaticTablesHandler

prefecture_lk = Blueprint('prefecture_lk', __name__)


@prefecture_lk.route('/prefecture_lk')
def prefecture_cabinet():

    #  ------ create users ------
    # bank_account = models.BankAccount(**models.BankAccount.make_spec('user', None))
    # env.db.impl().session.add(bank_account)
    # prefecture = models.Prefecture(
    #     name='Костромская область',
    #     bank_account_id=bank_account.id,
    #     prefect_id=None,
    #     social_assistant_id=None,
    #     economic_assistant_id=None,
    # )
    # env.db.impl().session.add(prefecture)
    # env.db.impl().session.commit()
    # bank_account = models.BankAccount(**models.BankAccount.make_spec('user', None))
    # env.db.impl().session.add(bank_account)
    # city = models.City(
    #     name='Кострома',
    #     mayor_id=None,
    #     location='201',
    #     prefecture_id=prefecture.id,
    #     bank_account_id=bank_account.id
    # )
    # env.db.impl().session.add(city)
    # env.db.impl().session.commit()
    # bank_account = models.BankAccount(**models.BankAccount.make_spec('user', None))
    # env.db.impl().session.add(bank_account)
    # user = models.User(
    #     bank_account_id=bank_account.id,
    #     city_id=city.id,
    #     name='Илья',
    #     last_name='Кононров',
    #     login='ilya',
    #     password='qwerty00',
    #     sex='male',
    #     bonus=0,
    #     birthday=datetime.datetime(1990, 10, 10, tzinfo=CurrentTimezone)
    # )
    # env.db.impl().session.add(user)
    # bank_account = models.BankAccount(**models.BankAccount.make_spec('user', None))
    # env.db.impl().session.add(bank_account)
    # user2 = models.User(
    #     bank_account_id=bank_account.id,
    #     city_id=city.id,
    #     name='Никита',
    #     last_name='Козубай',
    #     login='nikita',
    #     password='qwerty01',
    #     sex='male',
    #     bonus=0,
    #     birthday=datetime.datetime(1990, 10, 10, tzinfo=CurrentTimezone)
    # )
    # env.db.impl().session.add(user2)
    # product = models.Product(category='money', name='надик', level=0)
    # apples = models.Product(category='food', name='яблоко', level=0)
    # env.db.impl().session.add(product)
    # env.db.impl().session.add(apples)
    # env.db.impl().session.commit()
    # StaticTablesHandler.prepare_products_to_bank_account(
    #     bank_account_id=user.bank_account_id,
    #     product_id=product.id,
    #     count=1000
    # )
    # StaticTablesHandler.prepare_products_to_bank_account(
    #     bank_account_id=user2.bank_account_id,
    #     product_id=product.id,
    #     count=1000
    # )
    # StaticTablesHandler.prepare_products_to_bank_account(
    #     bank_account_id=user.bank_account_id,
    #     product_id=apples.id,
    #     count=30
    # )
    # env.db.impl().session.commit()

    """Личный кабинет префектуры"""
    return render_template('main/prefecture_lk_page.html')
