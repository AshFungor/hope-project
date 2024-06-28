import typing

import flask
import flask_login

import sqlalchemy as orm

# database
import app.models as models
from app.env import env

from . import blueprints
from . import consumption


def get_products(account: int) -> list[typing.Tuple[models.Product, models.Product2BankAccount]] | str:
    try:
        products = env.db.impl().session.query(
            models.Product,
            models.Product2BankAccount
        ).filter(
            orm.and_(
                # money don't count as products
                models.Product2BankAccount.bank_account_id == account,
                models.Product.id != 1
            )
        ).join(
            models.Product, models.Product2BankAccount.product_id == models.Product.id
        ).filter(
            models.Product2BankAccount.count != 0
        )
    except Exception as error:
        return f'failed to get products on handles module: {__name__}; error: {error}'
    return products


def prepare_data(
        products: list[typing.Tuple[models.Product, models.Product2BankAccount]], 
        account_id: int, 
        template: str,
        message: str,
        exclude_filter: bool = False
    ) -> flask.Response:
    parsed, categories = [], []
    for product, account in products:
        parsed.append({
            'id': product.id,
            'category': product.category,
            'level': product.level,
            'name': product.name,
            'count': account.count,
            'consumable': product.category in consumption.norms and not exclude_filter
        })
        categories.append(product.category)

    return flask.render_template(template, products=parsed, categories=set(categories), account_id=account_id, message=message)


@blueprints.product.route('/products')
@flask_login.login_required
def get_user_products(message: str | None = None):
    products = get_products(flask_login.current_user.bank_account_id)
    return prepare_data(products, flask_login.current_user.bank_account_id, 'main/view_products.html', message)


@blueprints.product.route('/products4company')
@flask_login.login_required
def get_company_products(message: str | None = None):
    products = get_products(int(flask.request.args.get('company_bank_account', None)))
    return prepare_data(products, int(flask.request.args.get('company_bank_account', None)), 'main/view_product4company.html', message, True)
