from pathlib import Path
from flask import Flask, Blueprint

from app.context import AppContext


def create_app() -> Flask:
    app = Flask(__name__)
    ctx = AppContext(app, Path.cwd() / "app/deploy.yaml")

    ctx.logger.info("setting up blueprints")

    from app.api import Blueprints
    from app.extensions import FlaskExtensions

    for bp in vars(Blueprints).values():
        if isinstance(bp, Blueprint):
            ctx.logger.debug(f'registering blueprint: {bp.name}')
            app.register_blueprint(bp)

    FlaskExtensions.setup(ctx.config)
    return app
