import datetime

import flask
import flask_login

import app.models as models
import app.routes.blueprints as blueprints
import app.routes.person_account as accounts

from app.env import env

logger = env.logger.getChild(__name__)


@blueprints.goal_model.route('/goal/make', methods=['POST'])
def create_goal():
    data = []
    for field in ['bank_account_id', 'value', 'amount_on_setup']:
        if field not in flask.request.form:
            return flask.abort(443, description=f'missing field: {field}')
        data.append(flask.request.form[field])
    account, target, current = data
    last = models.Goal.get_last(int(account), True)
    if last:
        return flask.abort(443, description=f'goal for today is already present')
    try:
        env.db.impl().session.add(models.Goal(account, target, current))
        env.db.impl().session.commit()
    except Exception as error:
        env.db.impl().session.rollback()
        error_message = 'Something went wrong during goal creation. Error: %s' % error
        logger.error(error_message)
        return flask.abort(400, description=error_message)
    return flask.redirect(flask.url_for('main.index'))


@blueprints.goal_view.route('/make_goal', methods=['GET'])
@flask_login.login_required
def view_create_goal():
    account = flask.request.args.get('account', None)
    if account is None:
        account = flask_login.current_user.bank_account_id

    return flask.render_template(
        'main/goal.html',
        bank_account_id=account,
        current=accounts.get_money(account)
    )

