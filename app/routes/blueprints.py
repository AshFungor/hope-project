import flask


class Blueprints:
    csv = flask.Blueprint("csv", __name__)
    transactions = flask.Blueprint("transactions", __name__)
    accounts = flask.Blueprint("accounts", __name__)
    session = flask.Blueprint("session", __name__)
    main = flask.Blueprint("main", __name__)
    proposals = flask.Blueprint("proposals", __name__)
    goals = flask.Blueprint("goals", __name__)
    product = flask.Blueprint("product", __name__)
    master = flask.Blueprint("master", __name__)
    stats = flask.Blueprint("statistics", __name__)
