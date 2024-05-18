import datetime

from flask import Blueprint, render_template, url_for

from app.modules.database.validators import CurrentTimezone
from app.env import env

import models

person_lk = Blueprint('person_lk', __name__)

@person_lk.route('/person_lk')
def person_cabinet():
    
    accounts = []
    # create prefecture
    prefecture = models.Prefecture()
    account = models.BankAccount()
    account.id = 0
    accounts.append(account)
    prefecture.bank_account_id = accounts[-1].id
    # create city
    city = models.City()
    city.bank_account_id = accounts[-1].id
    city.location = 'city Kek'
    city.name = 'Lol and kek'
    city.prefecture_id = prefecture.id
    # finally, user...
    user = models.User(
        accounts[-1].id,
        city.id,
        'Kek person',
        'still kek',
        'kek_login',
        '##yo__^_^__cool',
        'other',
        0,
        datetime.datetime.now(CurrentTimezone)
    )

    for account in accounts:
        env.db.impl().session.add(account)
    env.db.impl().session.add(prefecture)
    env.db.impl().session.add(city)
    env.db.impl().session.add(user)
    env.db.impl().session.commit()
    """Личный кабинет пользователя"""
    return render_template('main/person_lk_page.html')
