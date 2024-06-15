import requests

import flask
import flask_login

import app.routes.blueprints as blueprints


blueprints.proposal_blueprint.route('/new_transaction', methods=['GET'])
flask_login.login_required
def new_transaction() -> flask.Response:
    # get user bank account id & make payload from it
    user_id = flask_login.current_user.bank_account_id
    payload = {
        'user': user_id
    }
    # make post to local address and get all data for transactions
    response = requests.post('http://localhost/transaction/view', json=payload).json()
    return flask.render_template('main/transaction_view.html', transactions=response)
