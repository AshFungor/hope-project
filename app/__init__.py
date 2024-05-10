from flask import Flask
from .config import Config

from .routes.main import main
from .routes.person_lk import person_lk
from .routes.company_lk import company_lk
from .routes.city_lk import city_lk
from .routes.prefecture_lk import prefecture_lk
from .routes.city_hall_lk import city_hall_lk
from .routes.master_lk import master_lk
from .routes.admin_lk import admin_lk


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(main)
    app.register_blueprint(person_lk)
    app.register_blueprint(company_lk)
    app.register_blueprint(city_lk)
    app.register_blueprint(prefecture_lk)
    app.register_blueprint(city_hall_lk)
    app.register_blueprint(master_lk)
    app.register_blueprint(admin_lk)

    return app

