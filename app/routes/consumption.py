# base
import json
import typing
import logging
import datetime
import itertools

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


def get_gradient(ratio: float, first: int = int('006064', base=16), second: int = int('2E7D32', base=16)):
    gen = hex(round(first * ratio + second * (1 - ratio)))[2:]
    return '#' + '0' * (6 - len(gen)) + gen


def get_consumers() -> typing.Tuple[models.User, dict[str, str]]:
    users = env.db.impl().session.execute(
        orm.select(models.User)
    ).scalars().all()

    result = []
    for user in users:
        mapper, count = {}, 0
        for cat in norms.keys():
            status, payload = models.Consumption.did_consume_enough(
                user.bank_account_id, cat, norms[cat], time_accounted[cat] 
            )

            count += status
            if status:
                mapper[cat] = 'употреблен'
            else:
                mapper[cat] = f'осталось употребить: {payload}'

        result.append((user, mapper, get_gradient(count / len(mapper))))

    return result


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


@blueprints.master_blueprint.route('/view_consumers', methods=['GET'])
def view_consumers():
    category = flask.request.args.get('category', 'all')
    mode = flask.request.args.get('limits', 'all')
    data = get_consumers()

    current = norms.keys()
    if not category.lower().startswith('all'):
        data = [
            (user, {category: mapper.get(category, '')}, lower) 
            for user, mapper, lower in data
        ]
        current = [category]

    new_data = []
    if mode.lower().startswith('limit-consumers'):
        for user, mapper, number in data:
            if all([mapper[cat].startswith('употреблен') for cat in current]):
                new_data.append((user, mapper, number))
    elif mode.lower().startswith('limit-non-consumers'):
        for user, mapper, number in data:
            if not all([mapper[cat].startswith('употреблен') for cat in current]):
                new_data.append((user, mapper, number))
    else:
        new_data = data
    data = new_data

    return flask.render_template(
        'main/view_consumption.html', 
        consumed=data, 
        categories=norms.keys(),
        current=current,
        batch_size=len(data)
    )