# base
import json
import math
import logging

# flask
import flask
import flask_login

# local
from app.env import env

import app.models as models
import app.routes.blueprints as blueprints

from . import proposal as handles


@blueprints.proposal_blueprint.route('/view_transactions', methods=['GET'])
@flask_login.login_required
def view_transaction():
    # get user bank account id & make payload from it
    user_id = flask_login.current_user.bank_account_id
    payload = {
        'user': user_id
    }
    response = json.loads(handles.view_proposal(payload).data)
    return flask.render_template('main/view_transaction.html', transactions=response)


@blueprints.proposal_blueprint.route('/history', methods=['GET'])
@flask_login.login_required
def view_history():
    offset = int(flask.request.args.get('offset', 0))
    length = int(flask.request.args.get('length', 10))
    user_id = flask_login.current_user.bank_account_id
    payload = {
        'user': user_id
    }
    response = json.loads(handles.view_proposal_history(payload).data)
    selected, pages = [], [{'offset': length * curr, 'length': length, 'num': curr} for curr in range(int(math.ceil(len(response) / length)))]
    for transaction in response[offset:offset + length]:
        selected.append(transaction)
    return flask.render_template('main/view_all_transactions.html', 
        transactions=selected, 
        prev_offset=max(offset - length, 0),
        prev_length=length,
        next_offset=min(max(0, len(response) - length), offset + length),
        next_length=length,
        pages=pages)


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


@blueprints.proposal_blueprint.route('/new_money_transaction', methods=['GET'])
@flask_login.login_required
def new_money_transaction():
    bank_account_id = flask.request.args.get("bank_account_id", None)
    if not bank_account_id:
        bank_account_id = flask_login.current_user.bank_account_id
    return flask.render_template('main/make_money_transaction.html', user_bank_account=bank_account_id)


@blueprints.transaction_blueprint.route('/transaction/parse/create', methods=['POST'])
def parse_new_transaction():
    mapper = {
        'seller-account': 'customer_account',
        'bank_account_id': 'seller_account',
        'product-name': 'product',
        'count': 'product_count',
        'amount': 'amount'
    }

    params = {}
    for key, value in mapper.items():
        if key not in flask.request.form:
            return flask.Response(f'missing form field: {key}', status=443)
        params[value] = flask.request.form.get(key, None)

    response = None
    try:
        response = handles.new_proposal(params)
    except Exception as error:
        logging.warning(f'service request failed in handles module: {__name__}; error: {error}')
    if response is not None and response.status_code != 200:
        logging.warning(f'message return code: {response.status_code}; message: ' + response.content.decode('UTF-8'))

    return flask.redirect(flask.url_for('accounts.person_account'))


@blueprints.transaction_blueprint.route('/transaction/parse/money/create', methods=['POST'])
def parse_new_money_transaction():
    mapper = {
        'seller-account': 'customer_account',
        'bank_account_id': 'seller_account',
        'amount': 'amount'
    }

    params = {}
    for key, value in mapper.items():
        if key not in flask.request.form:
            return flask.Response(f'missing form field: {key}', status=443)
        params[value] = flask.request.form.get(key, None)

    response = None
    try:
        response = handles.new_money_proposal(params)
    except Exception as error:
        logging.warning(f'service request failed in handles module: {__name__}; error: {error}')
    if response is not None and response.status_code != 200:
        logging.warning(f'message return code: {response.status_code}; message: ' + response.content.decode('UTF-8'))

    return flask.redirect(flask.request.headers.get('Referer'))


@blueprints.transaction_blueprint.route('/transaction/parse/money/create', methods=['POST'])
def parse_new_money_transaction():
    mapper = {
        'seller-account': 'customer_account',
        'bank_account_id': 'seller_account',
        'amount': 'amount'
    }

    params = {}
    for key, value in mapper.items():
        if key not in flask.request.form:
            return flask.Response(f'missing form field: {key}', status=443)
        params[value] = flask.request.form.get(key, None)

    response = None
    try:
        response = requests.post('http://nginx/transaction/money/create', json=params)
    except Exception as error:
        logging.warning(f'service request failed in handles module: {__name__}; error: {error}')
    if response is not None and response.status_code != 200:
        logging.warning(f'message return code: {response.status_code}; message: ' + response.content.decode('UTF-8'))

    return flask.redirect(flask.request.headers.get('Referer'))
