# env import must be always first (!!!)

from app.env import env

# flask
from flask import Flask
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
from zoneinfo import ZoneInfo

# base
import sys
import signal
import logging
import datetime
import tracemalloc

# local
from app.modules.database.handlers import Database
from app.modules.database.handlers import DatabaseType

import app.models as models

import app.routes.blueprints as blueprints


login_manager = LoginManager()
login_manager.login_view = 'session.authorization'
toolbar = DebugToolbarExtension()


@login_manager.user_loader
def load_user(user_id):
    return env.db.impl().session.query(models.User).get(user_id)


# close running threads, connections etc.
def cleanup(signum: int, stacktrace: tracemalloc.Frame) -> None:
    env.logging_listeners.stop()
    sys.exit(signum)


def create_app() -> Flask:

    signal.signal(signal.SIGINT, cleanup)

    logging.info("initializing Flask app")
    app = Flask(__name__)

    logging.info('set a secret key')
    env.assign_new('9e496eeb2bdcb0f0058cc5f6', 'SECRET_KEY')
    app.secret_key = env.get_var('SECRET_KEY')

    login_manager.init_app(app)
    app.permanent_session_lifetime = datetime.timedelta(minutes=30)

    logging.info("initializing csrf protect")
    csrf = CSRFProtect(app)

    logging.info("handling Database creation")
    env.assign_new(Database(DatabaseType.from_str(env.server_database_type), app), 'db')
    env.assign_new(ZoneInfo("Europe/Moscow"), "default_timezone")

    app.debug = env.debug = True if env.debug in ('True', 'true', 1) else False
    if app.debug:
        toolbar.init_app(app)

    logging.info("handling routes")

    list(map(lambda bp: app.register_blueprint(bp), blueprints.all_blueprints))

    csrf.exempt(blueprints.csv_blueprint)
    csrf.exempt(blueprints.transaction_blueprint)

    return app
