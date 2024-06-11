# base
import datetime

# flask
import flask
import flask_login

# local
from app.env import env
from app.modules.database.validators import CurrentTimezone
import app.models as models

proposal = flask.Blueprint('proposal', __name__)


proposal.route('/make_proposal', methods=['POST'])
def make_proposal():
    payload, data = flask.request.json, []
    # parse payload
    for field in ['seller_account', 'customer_account', 'product', 'product_count', 'amount']:
        if field not in payload:
            return flask.Response(f'missing argument: {field}', status=443)
        data.append(payload[field])

    seller_account, customer_account, product, count, amount = data
    product_entry = env.db.impl().session.query(models.Product).filter_by(name=product).first()

    try:
        env.db.impl().session.add(models.Transaction(
            product_entry.id,
            int(customer_account),
            int(seller_account),
            int(count),
            int(amount),
            'created',
            datetime.datetime.now(tz=CurrentTimezone),
            datetime.datetime.now(tz=CurrentTimezone)
        ))
        env.db.impl().session.commit()
    except ValueError as value_error:
        return flask.Response(f'error validating input: {value_error}', status=443)
    
    return flask.Response('successful', status=200)

    
proposal.route('/proposal/new', methods=['GET'])
def proposal():
    # add frontend here later
    pass