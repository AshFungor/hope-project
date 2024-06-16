# base
import requests

# flask
import flask
import flask_login

# local
from app.env import env

import app.models as models
import app.routes.blueprints as blueprints


@blueprints.proposal_blueprint.route('/view_transactions', methods=['GET'])
@flask_login.login_required
def view_transaction():
    # get user bank account id & make payload from it
    user_id = flask_login.current_user.bank_account_id
    payload = {
        'user': user_id
    }
    # make post to local address and get all data for transactions
    response = requests.post('http://nginx/transaction/view', json=payload).json()
    return flask.render_template('main/view_transaction.html', transactions=response)


@blueprints.proposal_blueprint.route('/new_transaction', methods=['GET'])
@flask_login.login_required
def new_transaction():
    # get all products
    products = env.db.impl().session.query(models.Product).all()
    env.db.impl().session.commit()

    data = []
    for number, product in zip(range(len(products)), products):
        data.append(
            { 'name': product.name, 'number': number }
        )

    bank_account_id = flask.request.args.get("bank_account_id", None)
    if not bank_account_id:
        bank_account_id = flask_login.current_user.bank_account_id
    return flask.render_template('main/make_transaction.html', user_bank_account=bank_account_id, products=data)
