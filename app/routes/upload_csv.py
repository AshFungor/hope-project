import logging
import flask
import io

import pandas as pd

from app.env import env

import app.routes.blueprints as blueprints
import app.modules.database.static as static


def parse(payload: bytes) -> pd.DataFrame | flask.Response:
    frame = pd.read_csv(io.StringIO(payload.decode('UTF-8')), index_col=0)
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
    if added < result.shape[0]:
        env.db.impl().session.rollback()
        return flask.Response(status=443)
    env.db.impl().session.commit()
    return flask.Response(status=200)


@blueprints.csv_blueprint.route('/upload/csv/prefectures', methods=['POST'])
def parse_prefectures():
    result = parse(flask.request.data)
    if isinstance(result, flask.Response):
        return result
    added = static.StaticTablesHandler.prepare_prefectures(result)
    if added < result.shape[0]:
        env.db.impl().session.rollback()
        return flask.Response(status=443)
    env.db.impl().session.commit()
    return flask.Response(status=200)


@blueprints.csv_blueprint.route('/upload/csv/cities', methods=['POST'])
def parse_cities():
    result = parse(flask.request.data)
    if isinstance(result, flask.Response):
        return result
    added = static.StaticTablesHandler.prepare_cities(result)
    if added < result.shape[0]:
        env.db.impl().session.rollback()
        return flask.Response(status=443)
    env.db.impl().session.commit()
    return flask.Response(status=200)


@blueprints.csv_blueprint.route('/upload/csv/products', methods=['POST'])
def parse_products():
    result = parse(flask.request.data)
    if isinstance(result, flask.Response):
        return result
    added = static.StaticTablesHandler.prepare_products(result)
    if added < result.shape[0]:
        env.db.impl().session.rollback()
        return flask.Response(status=443)
    env.db.impl().session.commit()
    return flask.Response(status=200)