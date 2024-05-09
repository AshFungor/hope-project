from flask import Flask
from .config import Config

from .routes.main import main
from .routes.person_lk import person_lk

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(main)
    app.register_blueprint(person_lk)

    return app
