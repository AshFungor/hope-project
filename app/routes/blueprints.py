import flask

# back-end
csv_blueprint = flask.Blueprint('csv', __name__)
transaction_blueprint = flask.Blueprint('transaction', __name__)

# front-end
accounts_blueprint = flask.Blueprint('accounts', __name__)
session_blueprint = flask.Blueprint('session', __name__)
main = flask.Blueprint('main', __name__)
