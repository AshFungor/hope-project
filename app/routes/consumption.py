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
import app.routes.income as income
import app.routes.user_products as products


norms = {
    'FOOD': 1,
    'CLOTHES': 1,
    'TECHNIC': 1
}

defaults = {
    'FOOD': 120,
    'CLOTHES': 160,
    'TECHNIC': 200
}

time_accounted = {
    'FOOD': datetime.timedelta(days=1),
    'CLOTHES': datetime.timedelta(days=2),
    'TECHNIC': datetime.timedelta(days=4)
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


def collect_consumers(
    data: typing.Tuple[models.User, dict[str, str]], 
    full_mapping: dict[str, str]
) -> typing.Tuple[bool, str]:
    fillers = {}
    for mapped in full_mapping:
        if mapped not in norms:
            return f'ошибка: категория {mapped} не находиться в списке потребляемых ' + ', '.join(mapped.keys())
        match = env.db.impl().session \
            .query(models.Product) \
            .filter(orm.and_(
                models.Product.category == mapped,
                models.Product.level == 1
                )
            ).first()
        if match is None:
            return False, f'для категории {mapped} необходим товар с уровнем 1'
        fillers[mapped] = match
    count = 0
    for user, mappings, _ in data:
        for mapped in mappings:
            if mapped not in full_mapping:
                return False, f'ошибка: категория {mapped} не находиться в списке полных ' + ', '.join(full_mapping.keys())
            try:
                status, _ = models.Consumption.did_consume_enough(
                    user.bank_account_id, 
                    mapped, 
                    norms[mapped],
                    time_accounted[mapped]
                )
                if status:
                    continue
                env.db.impl().session.add(models.Consumption(
                    user.bank_account_id,
                    fillers[mapped].id,
                    norms[mapped],
                    datetime.datetime.now(tz=CurrentTimezone) - \
                        datetime.timedelta(days=1)
                ))
                account = env.db.impl().session \
                    .query(models.Product2BankAccount) \
                    .get((user.bank_account_id, 1))
                account.count -= defaults[mapped]
                count += 1
            except Exception as error:
                env.db.impl().session.rollback()
                return False, f'error: {error}'
    env.db.impl().session.commit()
    return True, f'потребление успешно: обработано {count} пользователей'


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
    is_selector = flask.request.args.get('selectors', 'OFF').upper().startswith('ON')
    is_collector = flask.request.args.get('collector', 'OFF').upper().startswith('ON')

    category = flask.request.args.get('category', 'all') if is_selector else 'all'
    mode = flask.request.args.get('limits', 'all') if is_selector else 'all'
    category = flask.request.args.get('collecting-category', 'all') if is_collector else category

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
    initial_size = len(data)
    data = new_data

    message = None
    if is_collector:
        cats = []
        if category.lower().startswith('all'):
            cats = norms.keys()
        else:
            cats = [category]
        status, message = collect_consumers(data, cats)
        if status:
            logging.info(f'потребление для категории {category} успешно')
        else:
            logging.warning(f'потребление для категории {category} не успешно, ошибка: {message}')

    return flask.render_template(
        'main/view_consumption.html', 
        consumed=data, 
        categories=norms.keys(),
        current=current,
        batch_size=len(data),
        initial_batch_size=initial_size,
        message=message
    )


@blueprints.proposal_blueprint.route('/view_consumption', methods=['GET'])
@flask_login.login_required
def view_consumption():
    account = flask.request.args.get('account', None)
    if account is None:
        account = flask_login.current_user.bank_account_id

    consumption_data = env.db.impl().session.query(
        models.Consumption,
        models.Product
    ).join(
        models.Product,
        models.Product.id == models.Consumption.product_id
    ).filter(
        models.Consumption.bank_account_id == account
    ).order_by(
        orm.desc(models.Consumption.consumed_at)
    ).all()

    payload = []
    for consumed, product in consumption_data:
        row = {}
        if datetime.time.max \
            > consumed.consumed_at.time() > \
            datetime.time(hour=18) \
        :
            row['Автоматическое списание'] = 'да'
            row['Цена автоматического списания'] = \
                norms[product.category] * defaults[product.category]
            row['Время потребления'] = \
                (consumed.local_consumed_at + datetime.timedelta(days=1)) \
                    .strftime('%d/%m/%Y %H:%M:%S')
        else:
            row['Автоматическое списание'] = 'нет'
            row['Цена автоматического списания'] = '-'
            row['Время потребления'] = \
                consumed.local_consumed_at.strftime('%d/%m/%Y %H:%M:%S')
        row['Категория'] = product.category
        payload.append(row)

    return flask.render_template(
        'main/view_all_consumption.html',
        payload=payload
    )
        
    