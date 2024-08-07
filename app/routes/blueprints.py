import flask

# back-end
csv_blueprint = flask.Blueprint('csv', __name__)
transaction_blueprint = flask.Blueprint('transaction', __name__)
goal_model = flask.Blueprint('goal_model', __name__)
stats = flask.Blueprint('statistics', __name__)

# front-end
# личные кабинеты
accounts_blueprint = flask.Blueprint('accounts', __name__)
# страница входа, ...
session_blueprint = flask.Blueprint('session', __name__)
# главная страница
main = flask.Blueprint('main', __name__)
# транзакции
proposal_blueprint = flask.Blueprint('proposal', __name__)
goal_view = flask.Blueprint('goal_view', __name__)
product = flask.Blueprint('product', __name__)
# для действий мастера игры
master_blueprint = flask.Blueprint('master', __name__)

all_blueprints = (
    csv_blueprint,
    transaction_blueprint,
    accounts_blueprint,
    session_blueprint,
    main,
    proposal_blueprint,
    goal_view,
    goal_model,
    product,
    master_blueprint,
    stats
)
