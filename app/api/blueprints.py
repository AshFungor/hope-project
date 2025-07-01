import flask


class Blueprints:
    loader = flask.Blueprint("loader", __name__)
    transactions = flask.Blueprint("transactions", __name__)
    session = flask.Blueprint("session", __name__)
    goal = flask.Blueprint("goal", __name__)
    product = flask.Blueprint("product", __name__)
    master = flask.Blueprint("master", __name__)
    company = flask.Blueprint("company", __name__)
