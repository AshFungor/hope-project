'''
Part of users/companies are usually part of overseeing the game process
and commonly are excluded from user stats. 
'''

import numpy as np
import sqlalchemy as orm

from app.env import env

import app.models as models


def users() -> list[int]:
    accounts = env.db.impl().session.query(
        models.BankAccount
    ).join(
        models.User, models.BankAccount.id == models.User.bank_account_id
    )

    return [account.id for account in accounts]


def high_rule() -> list[int]:
    # exclude admins
    admins = env.db.impl().session.query(
        models.User
    ).filter(
        models.User.is_admin == True
    ).all()
    # exclude companies by admins
    companies = env.db.impl().session.query(
        models.Company
    ).join(
        models.User2Company, models.User2Company.company_id == models.Company.id
    ).filter(
        models.User2Company.user_id.in_([admin.id for admin in admins])
    ).all()
    # exclude cities where admins live
    cities = env.db.impl().session.query(
        models.City
    ).filter(
        models.City.id.in_([admin.city_id for admin in admins])
    ).all()
    # get all accounts for these
    accounts = env.db.impl().session.query(
        models.BankAccount
    ).filter(
        orm.or_(
            models.BankAccount.id.in_([admin.bank_account_id for admin in admins]),
            models.BankAccount.id.in_([city.bank_account_id for city in cities]),
            models.BankAccount.id.in_([company.bank_account_id for company in companies])
        )
    ).all()

    return [account.id for account in accounts]