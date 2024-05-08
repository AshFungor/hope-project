from flask import Flask
from .config import Config

from .routes.main import main


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(main)

    return app
