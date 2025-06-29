import datetime
import logging
import flask
import io

import sqlalchemy as orm
import pandas as pd

from app.env import env

import app.models as models
import app.routes.blueprints as blueprints
import app.modules.database.static as static


logger = logging.Logger(__name__)


def parse(payload: bytes) -> pd.DataFrame | flask.Response:
    frame = pd.read_csv(io.StringIO(payload.decode('UTF-8')), sep=';')
    if frame.isnull().any(axis=None):
        logging.warning(f'received unparsed objects: \n{frame}')
        return flask.Response(status=443)
    return frame


@blueprints.csv_blueprint.route('/upload/csv/users', methods=['POST'])
def parse_users():
    result = parse(flask.request.data)
    if isinstance(result, flask.Response):
        return result
    added = static.StaticTablesHandler.prepare_users(result)
    if isinstance(added, str):
        return flask.Response(added, status=443)
    env.db.impl().session.commit()
    return flask.Response(status=200)


@blueprints.csv_blueprint.route('/upload/csv/prefectures', methods=['POST'])
def parse_prefectures():
    result = parse(flask.request.data)
    if isinstance(result, flask.Response):
        return result
    added = static.StaticTablesHandler.prepare_prefectures(result)
    if isinstance(added, str):
        return flask.Response(added, status=443)
    env.db.impl().session.commit()
    return flask.Response(status=200)


@blueprints.csv_blueprint.route('/upload/csv/cities', methods=['POST'])
def parse_cities():
    result = parse(flask.request.data)
    if isinstance(result, flask.Response):
        return result
    added = static.StaticTablesHandler.prepare_cities(result)
    if isinstance(added, str):
        return flask.Response(added, status=443)
    env.db.impl().session.commit()
    return flask.Response(status=200)


@blueprints.csv_blueprint.route('/upload/csv/products', methods=['POST'])
def parse_products():
    result = parse(flask.request.data)
    if isinstance(result, flask.Response):
        return result
    added = static.StaticTablesHandler.prepare_products(result)
    if isinstance(added, str):
        return flask.Response(added, status=443)
    env.db.impl().session.commit()
    return flask.Response(status=200)


@blueprints.csv_blueprint.route('/lol_kek', methods=['GET'])
def lol_kek_azaza():
    upper = datetime.datetime(year=2024, month=7, day=4, hour=9, minute=35)
    down = datetime.datetime(year=2024, month=7, day=4, hour=9, minute=40)

    consumed = env.db.impl().session.query(
        models.Product2BankAccount,
        models.Consumption
    ).join(
        models.Product2BankAccount,
        models.Product2BankAccount.bank_account_id == models.Consumption.bank_account_id
    ).filter(
        orm.and_(
            models.Product2BankAccount.product_id == 1,
            models.Consumption.product_id == 36,
            models.Consumption.consumed_at > down,
            models.Consumption.consumed_at < upper
        )
    ).all()

    for account, consume in consumed:
        account.count += consume.count * 200
        env.db.impl().session.delete(consume)

    env.db.impl().session.commit()
    return flask.Response(status=200)


@blueprints.csv_blueprint.route('/kek_lol', methods=['POST'])
def kek_lol():
    result: pd.DataFrame = parse(flask.request.files['file'].read())
    if isinstance(result, flask.Response):
        return result
    
    users = env.db.impl().session.query(models.User).all()
    cities = env.db.impl().session.query(models.City).all()

    logging.info(result.shape, result.sample(1))

    count = 0
    for login, prefecture in result.itertuples(index=False):
        p = False
        count += 1
        for user in users:
            if user.login != login:
                continue

            m_city = None
            for city in cities:
                if city.name == prefecture:
                    m_city = city

            user.city_id = m_city.id
            p = True

        if not p:
            return f'kek lol failed: {login} not found', 400

    env.db.impl().session.commit() 
    return f"ok, updated: {count}", 200
