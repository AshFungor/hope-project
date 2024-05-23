import flask
import json
import io

import pandas as pd

from app.env import env
from app.modules.database.static import StaticTablesHandler

csv = flask.Blueprint('csv', __name__)


def parse(payload: json, field: str) -> pd.DataFrame | flask.Response:
    frame = pd.read_csv(io.StringIO(payload[field]), sep=';')
    if any(frame.isna()):
        return flask.Response(status=443)
    return frame


@csv.route('/upload/csv/users', methods=['POST'])
def parse_users():
    result = parse(json.loads(flask.request.json), 'Users')
    if isinstance(result, flask.Response):
        return result
    added = StaticTablesHandler.prepare_users(result)
    if added < result.rows:
        env.db.impl().session.rollback()
        return flask.Response(status=443)
    env.db.impl().session.commit()
    return flask.Response(status=200)


@csv.route('/upload/csv/prefectures', methods=['POST'])
def parse_prefectures():
    result = parse(json.loads(flask.request.json), 'Prefectures')
    if isinstance(result, flask.Response):
        return result
    added = StaticTablesHandler.prepare_prefectures(result)
    if added < result.rows:
        env.db.impl().session.rollback()
        return flask.Response(status=443)
    env.db.impl().session.commit()
    return flask.Response(status=200)


@csv.route('/upload/csv/cities', methods=['POST'])
def parse_cities():
    result = parse(json.loads(flask.request.json), 'Cities')
    if isinstance(result, flask.Response):
        return result
    added = StaticTablesHandler.prepare_cities(result)
    if added < result.rows:
        env.db.impl().session.rollback()
        return flask.Response(status=443)
    env.db.impl().session.commit()
    return flask.Response(status=200)