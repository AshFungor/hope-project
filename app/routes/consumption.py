# base
import json
import logging
import datetime

# flask
import flask
import sqlalchemy as orm

# local
from app.env import env
from app.modules.database.validators import CurrentTimezone

import app.models as models
import app.routes.blueprints as blueprints
import app.modules.database.static as static
import app.routes.user_products as products


norms = {
    'FOOD': 1
}

def redirect_to_original(original: str, string: str) -> flask.Response:
    if original is None or original.startswith('5'):
        return products.get_user_products(string)
    return products.get_company_products(string)

@blueprints.product.route('/consume_product', methods=['POST'])
def consume():
    data = []
    for field in ['product', 'account']:
        if field not in flask.request.form:
            return flask.Response(f'missing form field: {field}')
        data.append(flask.request.form[field])

    product, account = map(int, data)
    named = env.db.impl().session.query(models.Product).get(product)

    if named.category not in norms:
        return flask.Response(f'продукт {named.name} не может быть употреблен', status=443)

    status, payload = models.Consumption.did_consume_enough(account, product, named, norms.get(named.category, 0), True)

    if isinstance(payload, str):
        logging.warning(f'internal error: {payload}')
        return flask.Response(status=500)
    
    # payload shows how much more we need to consume
    products = env.db.impl().session.execute(
        orm.select(
            models.Product2BankAccount
        ).filter(
            orm.and_(
                models.Product2BankAccount.bank_account_id == account,
                models.Product2BankAccount.product_id == product
            )
        )
    ).first()
    has = products.count

    original = flask.request.args.get('for', None)
    if not status:
        try:
            products.count -= min(has, payload)
            env.db.impl().session.add(models.Consumption(
                account, product, payload, datetime.datetime.now(tz=CurrentTimezone)
            ))
            env.db.impl().session.commit()
        except Exception as error:
            return redirect_to_original(original, 'ошибка потребления')
    else:
        return redirect_to_original(original, 'норма товара уже употреблена')
        
    if has < payload:
        return redirect_to_original(original, f'недостаточно товаров на счету: {payload - has}')
    return redirect_to_original(original, 'потребление успешно')


