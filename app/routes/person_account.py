import copy

import flask
import flask_login

import sqlalchemy as orm

from app.env import env

# local
import app.routes.blueprints as blueprints
import app.models as models


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
    setattr(current_user, 'money', get_money(current_user.bank_account_id))
    setattr(current_user, 'full_name', current_user.full_name_string)
    specs = []

    mapper = {
        'bank_account_id': 'номер банковского счета',
        'money': 'баланс счета',
        'full_name': 'полное имя',
        'login': 'логин',
        'birthday': 'день рождения',
    }

    for spec in mapper:
        specs.append({'name': mapper[spec], 'value': getattr(current_user, spec)})
    return flask.render_template('main/person_account_page.html', user_spec=specs)


