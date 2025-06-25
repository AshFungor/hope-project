import flask
import sqlalchemy as orm

from flask import render_template
from flask_login import current_user, login_required

from app.routes import Blueprints
from app.context import function_context, AppContext
from app.models import Product, Product2BankAccount, City, Company, Office, Prefecture


@Blueprints.accounts.route("/city")
@login_required
@function_context
def city(ctx: AppContext):
    city_id = current_user.city_id
    city: City = ctx.database.session.get_one(city_id)

    residents = ctx.database.session.execute(
        orm
        .select(Product.name, Product2BankAccount.count)
        .join(Product2BankAccount, Product2BankAccount.product_id == Product.id)
        .filter(Product2BankAccount.bank_account_id == city.bank_account_id)
    ).all()
    companies = ctx.database.session.execute(
        orm
        .select(Company.name)
        .join(Office, Office.company_id == Company.id)
        .filter(Office.city_id == city_id)
    ).all()

    if city is None:
        ctx.logger.warning(f"error: city {city_id} was not found")
        return flask.abort(400, description="An error occurred while rendering the city page")

    prefecture = ctx.database.session.scalar(
        orm
        .select(Prefecture.name)
        .filter_by(Prefecture.id == city.prefecture_id)
    )

    if prefecture is None:
        ctx.logger.warning(f"error: prefecture {city.prefecture_id} was not found")
        return flask.abort(400, description="An error occurred while rendering the city page")

    products = ctx.database.session.execute(
        orm
        .select(Product.name, Product2BankAccount.count)
        .join(Product2BankAccount, Product2BankAccount.product_id == Product.id)
        .filter(Product2BankAccount.bank_account_id == city.bank_account_id)
    ).all()
    balance = products[0].count

    return render_template(
        "accounts/city.html",
        balance=balance,
        city=city,
        mayor=city.mayor,
        residents=residents,
        products=products,
        companies=companies,
        prefecture=prefecture,
    )
