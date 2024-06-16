import datetime

from flask import abort, redirect, request
from flask_login import login_required

from app.env import env
from app.models.helpers import get_last_goal_by_bank_account
from app.models.user import Goal
from app.routes.blueprints import goal

logger = env.logger.getChild(__name__)


@goal.route('/goal/<int:id>', methods=['GET'])
def get_goal(): ...


@goal.route('/goal', methods=['POST'])
def create_goal():
    form_fields = ('bank_account_id', 'value', 'amount_on_setup')
    bank_account_id, value, amount_on_setup = (
        int(request.form.get(field)) if request.form.get(field) else None
        for field in form_fields
    )
    missing_variables = [
        field
        for field, value in zip(form_fields, (bank_account_id, value, amount_on_setup))
        if value is None
    ]
    if len(missing_variables):
        return abort(
            400,
            description=f'Missing values for goal creation: {", ".join(missing_variables)}',
        )
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
def update_goal(): ...
