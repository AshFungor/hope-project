import datetime

from flask import Blueprint, abort, redirect, request
from flask_login import login_required

from app.env import env
from app.models.helpers import get_last_goal_by_bank_account
from app.models.user import Goal

logger = env.logger.getChild(__name__)
goal = Blueprint('goal', __name__)


@goal.route('/goal/<int:id>', methods=['GET'])
@login_required
def get_goal(): ...


@goal.route('/goal', methods=['POST'])
@login_required
def create_goal():
    bank_account_id = int(request.form.get('bank_account_id', 0))
    value = int(request.form.get('value', 0))
    amount_on_setup = int(request.form.get('amount_on_setup', 0))
    if not (bank_account_id and value and amount_on_setup):
        return abort(400, description='Missing some values for goal creation')
    last_goal = get_last_goal_by_bank_account(bank_account_id)
    if last_goal:
        if last_goal.amount_on_validate:
            amount_on_setup = last_goal.amount_on_validate
    created_at = request.form.get('created_at')
    if not created_at:
        created_at = datetime.datetime.now(env.default_timezone)
    goal_obj = Goal(bank_account_id, value, amount_on_setup, created_at=created_at)
    try:
        session = env.db.impl().session
        session.add(goal_obj)
        session.commit()
    except Exception as e:
        logger.error('Something went wrong during goal creation. Error: %s', e)
        return abort(
            400, description='Something went wrong during goal creation. Error: %s' % e
        )
    return redirect(request.headers.get('Referer'))


@goal.route('/goal/<int:id>', methods=['PUT'])
@login_required
def update_goal(): ...
