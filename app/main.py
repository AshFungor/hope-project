# env import must be always first (!!!)
from app.env import env

# flask
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# base
import sys
import logging
import signal
import tracemalloc

# local
from app.modules.database.handlers import Database
from app.modules.database.handlers import MockStorage


# close running threads, connections etc.
def cleanup(signum: int, stacktrace: tracemalloc.Frame) -> None:
    env.logging_listeners.stop()
    sys.exit(signum)


def create_app():

    signal.signal(signal.SIGINT, cleanup)

    logging.info("initializing Flask app")
    app = Flask(__name__)

    # merge received through Env config with default one that app has 
    app.config.update(env.make_flask_config(env.env_flask_vars))

    logging.info("handling Database creation")
    env.assign_new(None, 'db')
    if env.server_use_mocked_database:
        mockedHandle = MockStorage(app)
        env.db = Database(mockedHandle)
    else:
        handle = SQLAlchemy()
        handle.init_app(app)
        with app.app_context():
            handle.create_all()
        env.db = Database(handle)

    logging.info("handling routes")

    from app.routes.main import main
    from app.routes.person_lk import person_lk
    from app.routes.company_lk import company_lk
    from app.routes.city_lk import city_lk
    from app.routes.prefecture_lk import prefecture_lk
    from app.routes.city_hall_lk import city_hall_lk
    from app.routes.master_lk import master_lk
    from app.routes.admin_lk import admin_lk
    from app.routes.login import login

    app.register_blueprint(main)
    app.register_blueprint(person_lk)
    app.register_blueprint(company_lk)
    app.register_blueprint(city_lk)
    app.register_blueprint(prefecture_lk)
    app.register_blueprint(city_hall_lk)
    app.register_blueprint(master_lk)
    app.register_blueprint(admin_lk)
    app.register_blueprint(login)

    return app
