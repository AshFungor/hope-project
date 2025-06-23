import datetime
import logging

from flask import Flask
from pathlib import Path

import app.routes.blueprints as blueprints

from app.extensions import FlaskExtensions
from app.context import AppContext, context



def create_app() -> Flask:
    app = Flask(__name__)
    ctx = AppContext(app, Path.cwd() / "app/deploy.yaml")

    logging.info("setting up blueprints")
    for bp in blueprints.all_blueprints:
        app.register_blueprint(bp)

    FlaskExtensions.setup(ctx.config)
    return app
