import datetime

from flask import Blueprint, render_template, url_for

from app.modules.database.validators import CurrentTimezone
from app.env import env

# models and parsing
import models
import os, csv, dateutil


from app.modules.database.create_tables import TbCreator


person_lk = Blueprint('person_lk', __name__)

@person_lk.route('/person_lk')
def person_cabinet():

    # users_id: 5, 6
    if not TbCreator.check:
        TbCreator.create_all_start_tables()
        product_id = TbCreator.create_product('электроника', 'playstation 5', 2)
        TbCreator.create_products_to_bank_account(
            bank_account_id=env.db.impl().session.query(models.User).get(1).bank_account_id,
            product_id=product_id,
            count=1
        )

    # accounts = []
    # # create prefecture
    # prefecture = models.Prefecture()
    # account = models.BankAccount()
    # account.id = 0
    # accounts.append(account)
    # prefecture.bank_account_id = accounts[-1].id
    # # create city
    # city = models.City()w
    # city.bank_account_id = accounts[-1].id
    # city.location = 'city Kek'
    # city.name = 'Lol and kek'
    # city.prefecture_id = prefecture.id
    # # finally, user...
    # time = datetime.datetime.now(CurrentTimezone)
    # user = models.User(
    #     accounts[-1].id,
    #     city.id,
    #     'Кек',
    #     'Лол',
    #     'kek_login',
    #     '##yo__^_^__cool',
    #     'other',
    #     0,
    #     time
    # )
    #
    # for account in accounts:
    #     env.db.impl().session.add(account)
    # env.db.impl().session.add(prefecture)
    # env.db.impl().session.add(city)
    # env.db.impl().session.add(user)
    # env.db.impl().session.commit()
    """Личный кабинет пользователя"""
    return render_template('main/person_lk_page.html')


