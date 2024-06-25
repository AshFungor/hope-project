import typing

import sqlalchemy
import flask
import flask_login

# database
import app.models as models
from app.env import env

from . import blueprints


def get_products(account: int) -> list[typing.Tuple[models.Product, models.Product2BankAccount]] | str:
    try:
        products = env.db.impl().session.query(
            models.Product,
            models.Product2BankAccount
        ).filter(
            models.Product2BankAccount.bank_account_id == account
        ).join(
            models.Product, models.Product2BankAccount.product_id == models.Product.id
        ).filter(
            models.Product2BankAccount.count != 0
        )
    except Exception as error:
        return f'failed to get products on handles module: {__name__}; error: {error}'
    return products


@blueprints.product.route('/products')
@flask_login.login_required
def get_user_products():
    products = get_products(flask_login.current_user.bank_account_id)

    parsed,categories = [], []
    for product, account in products:
        parsed.append({
            'category': product.category,
            'level': product.level,
            'name': product.name,
            'count': account.count
        })
        categories.append(product.category)

    return flask.render_template('main/view_products.html', products=parsed, categories=set(categories))

@blueprints.product.route('/products4company')
@flask_login.login_required
def get_company_products():
    products = get_products(int(flask.request.args.get('company_bank_account', None)))

    parsed,categories = [], []
    for product, account in products:
        parsed.append({
            'category': product.category,
            'level': product.level,
            'name': product.name,
            'count': account.count
        })
        categories.append(product.category)

    return flask.render_template('main/view_product4company.html', products=parsed, categories=set(categories))
