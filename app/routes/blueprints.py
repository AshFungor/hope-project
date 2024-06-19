import flask

# back-end
csv_blueprint = flask.Blueprint('csv', __name__)
transaction_blueprint = flask.Blueprint('transaction', __name__)

# front-end
# личные кабинеты
accounts_blueprint = flask.Blueprint('accounts', __name__)
# страница входа, ...
session_blueprint = flask.Blueprint('session', __name__)
# главная страница
main = flask.Blueprint('main', __name__)
# транзакции
proposal_blueprint = flask.Blueprint('proposal', __name__)
goal = flask.Blueprint('goal', __name__)
# для действий мастера игры
master_blueprint = flask.Blueprint('master', __name__)

all_blueprints = (
    csv_blueprint,
    transaction_blueprint,
    accounts_blueprint,
    session_blueprint,
    main,
    proposal_blueprint,
    goal,
    master_blueprint,
)
