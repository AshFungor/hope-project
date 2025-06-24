import logging
import app.routes.blueprints as blueprints

from pathlib import Path
from flask import Flask

from app.context import AppContext
from app.extensions import FlaskExtensions


def create_app() -> Flask:
    app = Flask(__name__)
    ctx = AppContext(app, Path.cwd() / "app/deploy.yaml")

    logging.info("setting up blueprints")
    for bp in blueprints.Blueprints:
        app.register_blueprint(bp)

    FlaskExtensions.setup(ctx.config)
    return app
