import logging

import sqlalchemy
from flask import Blueprint, render_template, url_for
from flask_login import login_required, current_user

from app.env import env
import app.models as models

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints


@blueprints.accounts_blueprint.route('/city_lk')
@login_required
def city_cabinet():
    """Личный кабинет города!!"""

    #  get city and his mayor
    query_city = (
        sqlalchemy.select(
            models.City.id,
            models.City.name,
            models.City.location,
            models.City.mayor_id,
            models.City.bank_account_id
        )
        .filter(
            models.City.id == current_user.city_id
        )
    )
    city = env.db.impl().session.execute(query_city).first()
    if city.mayor_id:
        query_mayor = (
            sqlalchemy.select(
                models.User.name,
                models.User.last_name)
            .filter_by(id=city.mayor_id)
        )
        mayor = env.db.impl().session.execute(query_mayor).first()
    else:
        mayor = None

    # get residents of city
    query_residents = (
        sqlalchemy.select(
            models.User.name,
            models.User.last_name,
            models.User.bank_account_id)
        .filter_by(
            city_id=city.id)
    )
    residents = env.db.impl().session.execute(query_residents).all()

    # get products of city
    query_products = (
        sqlalchemy.select(
            models.Product.name,
            models.Product2BankAccount.count,
        )
        .join(models.Product2BankAccount, models.Product2BankAccount.product_id == models.Product.id)
        .filter(
            models.Product2BankAccount.bank_account_id == city.bank_account_id
        )
    )
    products = env.db.impl().session.execute(query_products)

    # get offices in city
    query_companies = (
        sqlalchemy.select(
            models.Company.name)
        .join(models.Office, models.Office.company_id == models.Company.id)
        .filter(models.Office.city_id == city.id)
    )
    companies = env.db.impl().session.execute(query_companies).all()
    return render_template('main/city_lk_page.html',
                           city=city,
                           mayor=mayor,
                           residents=residents,
                           products=products,
                           companies=companies)
