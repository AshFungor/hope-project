# base
import json
import logging
import datetime

# flask
import flask
import flask_login
import sqlalchemy as orm

# local
from app.env import env
from app.modules.database.validators import CurrentTimezone

import app.models as models
import app.routes.blueprints as blueprints
import app.modules.database.static as static
import app.routes.user_products as products


norms = {
    'FOOD': 1,
    'CLOTHES': 1,
    'TECHNIC': 1
}

time_accounted = {
    'FOOD': datetime.timedelta(days=1),
    'CLOTHES': datetime.timedelta(days=2),
    'TECHNIC': datetime.timedelta(days=3)
}

def redirect_to_original(original: str, string: str) -> flask.Response:
    if original is None or original.startswith('5'):
        return products.get_user_products(string)
    return products.get_company_products(string)


def get_current_user_bonus(level: int) -> int:
    if level <= 3: return level - 1
    return level


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

    status, payload = models.Consumption.did_consume_enough(
        account,  
        named.category, 
        norms.get(named.category, 0), 
        time_accounted.get(named.category, datetime.timedelta(days=1))
    )

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
    ).first()[0]
    has = products.count

    original = flask.request.args.get('for', None)
    if not status:
        try:
            products.count -= min(has, payload)
            env.db.impl().session.add(models.Consumption(
                account, product, payload, datetime.datetime.now(tz=CurrentTimezone)
            ))

            if original is None or original.startswith('5'):
                flask_login.current_user.bonus += get_current_user_bonus(named.level)

            env.db.impl().session.commit()
        except Exception as error:
            logging.warning(f'error on consumption: {error}')
            return redirect_to_original(original, 'ошибка потребления')
    else:
        return redirect_to_original(original, 'норма товара уже употреблена')
        
    if has < payload:
        return redirect_to_original(original, f'недостаточно товаров на счету: {payload - has}')
    return redirect_to_original(original, 'потребление успешно')


