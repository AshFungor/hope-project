# env import must be always first (!!!)
import datetime
import os

from app.env import env

# flask
from flask import Flask
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy


from app.routes.main import login_manager


# base
import sys
import logging
import signal
import tracemalloc

# local
from app.modules.database.handlers import Database
from app.modules.database.handlers import DatabaseType

from app.routes.main import main
from app.routes.person_lk import person_lk
from app.routes.company_lk import company_lk
from app.routes.city_lk import city_lk
from app.routes.prefecture_lk import prefecture_lk
from app.routes.city_hall_lk import city_hall_lk
from app.routes.master_lk import master_lk
from app.routes.admin_lk import admin_lk
from app.routes.login import login
from app.routes.transaction import transaction
from app.routes.upload_csv import csv
from app.routes.user_suggestions import user_suggestions
from app.routes.suggestion import suggestion


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

    logging.info("handling routes")

    app.register_blueprint(main)
    app.register_blueprint(person_lk)
    app.register_blueprint(company_lk)
    app.register_blueprint(city_lk)
    app.register_blueprint(prefecture_lk)
    app.register_blueprint(city_hall_lk)
    app.register_blueprint(master_lk)
    app.register_blueprint(admin_lk)
    app.register_blueprint(login)
    app.register_blueprint(transaction)
    app.register_blueprint(csv)
    app.register_blueprint(user_suggestions)
    app.register_blueprint(suggestion)

    return app
