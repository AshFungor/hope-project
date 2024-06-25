import logging
import typing

import flask
import sqlalchemy
from flask import Blueprint, render_template, url_for
from flask_login import login_required, current_user

from app.env import env
import app.models as models

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints

logger = env.logger.getChild(__name__)


def get_city(city_id: int) -> models.City | None:
    return env.db.impl().session.execute(
        sqlalchemy.select(
            models.City
        )
        .filter_by(
            id=city_id
        )
    ).scalars().first()


def get_city_residents(city_id: int) -> typing.Tuple[models.User] | None:
    return env.db.impl().session.execute(
        sqlalchemy.select(
            models.User.name,
            models.User.last_name,
            models.User.bank_account_id)
        .filter_by(
            city_id=city_id)
    ).all()


def get_products_and_count(bank_account: int) -> typing.Tuple[models.Product] | None:
    return env.db.impl().session.execute(
        sqlalchemy.select(
            models.Product.name,
            models.Product2BankAccount.count,
        )
        .join(models.Product2BankAccount, models.Product2BankAccount.product_id == models.Product.id)
        .filter(
            models.Product2BankAccount.bank_account_id == bank_account
        )
    ).all()


def get_city_companies(city_id: int) -> typing.Tuple[models.Company] | None:
    return env.db.impl().session.execute(
            sqlalchemy.select(
                models.Company.name)
            .join(models.Office, models.Office.company_id == models.Company.id)
            .filter(models.Office.city_id == city_id)
    ).all()


def get_city_prefecture(prefecture_id: int) -> models.Prefecture | None:
    return env.db.impl().session.execute(
        sqlalchemy.select(
            models.Prefecture.name
        )
        .filter_by(id=prefecture_id)
    ).scalars().first()


@blueprints.accounts_blueprint.route('/city_lk')
@login_required
def city_cabinet():
    """Личный кабинет города!!"""

    city_id = current_user.city_id

    city = get_city(city_id=city_id)
    residents = get_city_residents(city_id=city_id)
    companies = get_city_companies(city_id=city_id)
    if city is None:
        logger.warning(f'an error occurred while rendering the city page; '
                       f'reason: city was not found to represent the page')
        return flask.abort(
            400,
            descripstion='An error occurred while rendering the city page'
        )
    prefecture = get_city_prefecture(prefecture_id=city.prefecture_id)
    if prefecture is None:
        logger.warning(f'an error occurred while rendering the city page; '
                       f'reason: prefecture was not found to represent the page')
        return flask.abort(
            400,
            description='An error occurred while rendering the city page'
        )
    products = get_products_and_count(bank_account=city.bank_account_id)
    return render_template('main/city_lk_page.html',
                           city=city,
                           mayor=city.mayor,
                           residents=residents,
                           products=products,
                           companies=companies,
                           prefecture=prefecture
                           )

