# base
import json
import logging
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


@blueprints.transaction_blueprint.route('/transaction/create', methods=['POST'])
def new_proposal() -> flask.Response:
    payload, data = flask.request.json, []
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

    try:
        env.db.impl().session.add(models.Transaction(
            product_entry.id,
            int(customer_account),
            int(seller_account),
            int(count),
            int(amount),
            'created',
            datetime.datetime.now(tz=CurrentTimezone),
            datetime.datetime.now(tz=CurrentTimezone),
            ''
        ))
        env.db.impl().session.commit()
    except ValueError as value_error:
        return flask.Response(f'error validating input: {value_error}', status=443)
    
    return flask.Response('successful', status=200)


@blueprints.transaction_blueprint.route('/transaction/view', methods=['POST'])
def view_proposal():
    payload = flask.request.json
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
    .join(models.User, models.User.bank_account_id == models.Transaction.seller_bank_account_id)        \
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


@blueprints.transaction_blueprint.route('/transaction/decide', methods=['POST'])
def decide_on_proposal():
    payload = flask.request.json
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
