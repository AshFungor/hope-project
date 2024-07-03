import copy
import datetime

import flask
import flask_login

import sqlalchemy as orm

from app.env import env

# local
import app.routes.consumption as consumption
import app.routes.blueprints as blueprints
import app.models as models


def time_span_formatter(span: datetime.timedelta) -> str:
    return f'{span.days} дней'


def get_money(id: int) -> int:
    query = None
    try:
        query = env.db.impl().session.query(models.Product2BankAccount).filter(
            orm.and_(
                models.Product2BankAccount.bank_account_id == id,
                models.Product2BankAccount.product_id == 1, # money
            )
        ).all()
        if len(query) != 1:
            return f'internal error: query returned more than 1 or less than 1 position: {len(query)}'
        return query[0].count
    except Exception as error:
        return f'error getting products for user {id}; looked up 1; error: {error}'


@blueprints.accounts_blueprint.route('/person_account')
@flask_login.login_required
def person_account():
    current_user = copy.deepcopy(flask_login.current_user)

    goal = models.Goal.get_last(current_user.bank_account_id, True)
    if goal is None:
        return flask.redirect(flask.url_for('goal_view.view_create_goal'))

    setattr(goal, 'rate', goal.get_rate(get_money(current_user.bank_account_id)))

    setattr(current_user, 'money', get_money(current_user.bank_account_id))
    setattr(current_user, 'full_name', current_user.full_name_string)
    specs = []
    balance = get_money(current_user.bank_account_id)
    mapper = {
        'bank_account_id': 'номер банковского счета',
        'money': 'баланс счета',
        'full_name': 'полное имя',
        'login': 'логин',
        'birthday': 'день рождения',
        'bonus': 'бонус'
    }

    consumption_data = {}
    for name in consumption.norms:
        status, left = models.Consumption.did_consume_enough(
            current_user.bank_account_id,
            name, 
            consumption.norms[name],
            consumption.time_accounted[name]
        )
        consumption_data[name] = {
            'Употребление': 'да' if status else 'нет',
            'Норма употребления': consumption.norms[name],
            'Эпизодичность': time_span_formatter(
                consumption.time_accounted[name]
            )
        }
    

    for spec in mapper:
        specs.append({'name': mapper[spec], 'value': getattr(current_user, spec)})
    return flask.render_template(
        'main/person_account_page.html', 
        user_spec=specs, 
        goal=goal, 
        balance=balance,
        consumption_data=consumption_data
    )


