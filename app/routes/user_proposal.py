import json
import flask
import datetime

import flask
import flask_login

from sqlalchemy import and_

import app.models as models
from app.env import env
from app.modules.database.validators import CurrentTimezone
from app.modules.database.static import StaticTablesHandler

user_proposal = flask.Blueprint('user_proposal', __name__)


@user_proposal.route('/proposal/view', methods=['POST'])
def view_user_proposals():
    payload = flask.request.json
    if 'user' not in payload:
        return flask.Response('user field id missing', status=443)
    
    user = int(payload['user'])
    proposals = env.db.impl().session.get().query(
        models.User.bank_account_id,
        models.Transaction.id,
        models.Transaction.amount,
        models.Transaction.count,
        models.Product.name
    )                                                                                                   \
    .filter(                                                                                            \
        and_(                                                                                           \
            models.Transaction.status == 'created',
            models.Transaction.updated_at >= datetime.datetime.now(tz=CurrentTimezone),
            models.Transaction.customer_bank_account_id == user)
        )                                       \
    .join(models.User, models.User.bank_account_id == models.Transaction.seller_bank_account_id)        \
    .join(models.Product, models.Product.id == models.Transaction.product_id)

    response = []
    for transaction_id, amount, count, product in proposals:
        response.append({
            'transaction_id': transaction_id,
            'amount': amount,
            'count': count,
            'product': product
        })
    return flask.Response(json.dump(response), status=200)


@user_proposal.route('/proposal/decide', methods=['POST'])
def decide_on_proposal():
    payload = flask.request.json
    if 'status' not in payload:
        return flask.Response('status field id missing', status=443)
    
    if 'transaction_id' not in payload:
        return flask.Response('status field id missing', status=443)
    
    status = payload['status']
    id = int(payload['transaction_id'])
    message, status = StaticTablesHandler.complete_transaction(id, status)

    if not status:
        return flask.Response(message, status=400)
    return flask.Response(message, status=200)

