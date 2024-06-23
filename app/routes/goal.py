import datetime

import flask
import flask_login

import app.models as models
import app.modules.database.validators as validators

from app.env import env
from app.routes.blueprints import goal

logger = env.logger.getChild(__name__)


@goal.route('/goal/make', methods=['POST'])
def create_goal():
    data = []
    for field in ['bank_account_id', 'value', 'amount_on_setup']:
        if field not in flask.request.form:
            return flask.abort(443, description=f'missing field: {field}')
        data.append(flask.request.form[field])
    account, target, current = data
    last = models.Goal.get_last(int(account))
    if last:
        return flask.abort(443, description=f'goal for today is already present')
    try:
        session = env.db.impl().session.add(models.Goal(account, target, current))
        session.commit()
    except Exception as error:
        error_message = 'Something went wrong during goal creation. Error: %s' % error
        logger.error(error_message)
        return flask.abort(400, description=error_message)
    return flask.redirect(flask.request.headers.get('Referer'))

