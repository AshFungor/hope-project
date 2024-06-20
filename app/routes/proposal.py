# base
import json
import logging
import requests
import datetime

# flask
import flask
import sqlalchemy

# local
from app.env import env
from app.modules.database.validators import CurrentTimezone

import app.models as models
import app.routes.blueprints as blueprints
import app.modules.database.static as static


def handle_payload(passed: dict[str, str] | None, request: flask.Request):
    if passed is not None:
        return passed
    return request.json


def get_transactions_for(id: int, for_seller: bool = True):
    feature = 'seller_bank_account_id' if for_seller else 'customer_bank_account_id'
    return env.db.impl().session.query(
        models.User,
        models.Transaction,
        models.Product
    )                                                                                                   \
    .filter(getattr(models.Transaction, feature) == id)                                                 \
    .join(models.User, models.User.bank_account_id == getattr(models.Transaction, feature))             \
    .join(models.Product, models.Product.id == models.Transaction.product_id)                           \
    .all()


@blueprints.transaction_blueprint.route('/transaction/create', methods=['POST'])
def new_proposal(payload: dict[str, str] | None = None) -> flask.Response:
    payload, data = handle_payload(payload, flask.request), []
    # parse payload
    for field in ['seller_account', 'customer_account', 'product', 'product_count', 'amount']:
        if field not in payload:
            return flask.Response(f'missing argument: {field}', status=443)
        data.append(payload[field])

    seller_account, customer_account, product, count, amount = data
    product_entries = env.db.impl().session.query(models.Product).filter_by(name=product)

    if len(product_entries.all()) > 1:
        return flask.Response('product is not unique, database is corrupted', status=443)
    if not product_entries.all():
        return flask.Response(f'product with name = {product} not found', status=443)
    product_entry = product_entries.first()

    assigned_id = None
    try:
        transaction = models.Transaction(
            product_entry.id,
            int(customer_account),
            int(seller_account),
            int(count),
            int(amount),
            'created',
            datetime.datetime.now(tz=CurrentTimezone),
            datetime.datetime.now(tz=CurrentTimezone),
            ''
        )
        assigned_id = transaction.id
        env.db.impl().session.add(transaction)
        env.db.impl().session.commit()
    except Exception as error:
        env.db.impl().session.rollback()
        logging.warning(f'error while adding new transaction: {error}')
        return flask.Response(f'incorrect input', status=443)
    
    return flask.Response('success', status=200)


@blueprints.transaction_blueprint.route('/transaction/money/create', methods=['POST'])
def new_money_proposal(payload: dict[str, str] | None = None) -> flask.Response:
    payload, data = handle_payload(payload, flask.request), []
    # parse payload
    for field in ['seller_account', 'customer_account', 'amount']:
        if field not in payload:
            return flask.Response(f'missing argument: {field}', status=443)
        data.append(payload[field])

    seller_account, customer_account, amount = data
    try:
        transaction = models.Transaction(
            1,
            int(customer_account),
            int(seller_account),
            int(amount),
            int(amount),
            'created',
            datetime.datetime.now(tz=CurrentTimezone),
            datetime.datetime.now(tz=CurrentTimezone),
            ''
        )
        env.db.impl().session.add(transaction)

        # approve it
        message, status = transaction.process(True)
        if not status:
            env.db.impl().session.rollback()
            logging.warning(message)
            return flask.Response(message, status=443)
        else:
            logging.info(message)
        
        env.db.impl().session.commit()
        return flask.Response(message, status=200)
    except Exception as error:
        env.db.impl().session.rollback()
        logging.warning(f'error while completing transaction: {error}')
        return flask.Response(f'incorrect input', status=443)


@blueprints.transaction_blueprint.route('/transaction/view/current', methods=['POST'])
def view_proposal(payload: dict[str, str] | None = None):
    payload = handle_payload(payload, flask.request)
    if 'user' not in payload:
        return flask.Response('user field is missing', status=443)
    
    user = int(payload['user'])

    proposals = env.db.impl().session.query(
        models.User,
        models.Transaction,
        models.Product
    )                                                                                                   \
    .filter(                                                                                            \
        sqlalchemy.and_(                                                                                \
            models.Transaction.status == 'created',
            models.Transaction.customer_bank_account_id == user
        )
    )                                                                                                   \
    .join(models.User, models.User.bank_account_id == models.Transaction.customer_bank_account_id)      \
    .join(models.Product, models.Product.id == models.Transaction.product_id)                           \
    .all()

    response = []
    for user, transaction, product in proposals:
        response.append({
            'transaction_id': transaction.id,
            'amount': transaction.amount,
            'count': transaction.count,
            'product': product.name
        })
    return flask.Response(json.dumps(response, indent=4, sort_keys=True), status=200)


@blueprints.transaction_blueprint.route('/transaction/view/history', methods=['POST'])
def view_proposal_history(payload: dict[str, str] | None = None):
    payload = handle_payload(payload, flask.request)
    if 'user' not in payload:
        return flask.Response('user field is missing', status=443)
    
    user = int(payload['user'])

    seller_proposals = get_transactions_for(user, True)
    customer_proposals = get_transactions_for(user, False)

    response = []
    for proposals, side in [(seller_proposals, 'seller'), (customer_proposals, 'customer')]:
        for user, transaction, product in proposals:
            response.append({
                'transaction_id': transaction.id,
                'amount': transaction.amount,
                'count': transaction.count,
                'product': product.name,
                'status': transaction.status,
                'updated_at': transaction.updated_at.strftime('%d/%m/%Y %H:%M:%S'),
                'side': side,
                'is_money': product.id == 1
            })
    return flask.Response(json.dumps(response, indent=4, sort_keys=True), status=200)


@blueprints.transaction_blueprint.route('/transaction/decide', methods=['POST'])
def decide_on_proposal(payload: dict[str, str] | None = None):
    payload = handle_payload(payload, flask.request)
    if 'status' not in payload:
        return flask.Response('status field is missing', status=443)
    
    if 'transaction_id' not in payload:
        return flask.Response('status field is missing', status=443)
    
    status = payload['status']
    id = int(payload['transaction_id'])
    message, result = static.StaticTablesHandler.complete_transaction(id, status)

    logging.info(f'transaction {id} with status = {status}; completed: {result}; decision: {message}')

    if not result:
        return flask.Response(message, status=400)
    return flask.Response(message, status=200)
