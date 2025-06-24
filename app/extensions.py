from datetime import timedelta

from flask_login import LoginManager
from flask_wtf import CSRFProtect

import app.models as models
import app.routes.blueprints as blueprints
from app.context import AppConfig, AppContext, context


class FlaskExtensions:
    @classmethod
    def setup(cls, config: AppConfig):
        if config.flask_extensions.csrf:
            cls.__init_csrf()
        if config.flask_extensions.login_manager:
            cls.__init_login_manager()

    @classmethod
    @context
    def __init_csrf(cls, ctx: AppContext):
        ctx.logger.info("setting up CSRF protection")
        csrf = CSRFProtect(ctx.app)
        csrf.exempt(blueprints.csv)
        csrf.exempt(blueprints.transactions)

    @classmethod
    @context
    def __init_login_manager(cls, ctx: AppContext):
        ctx.logger.info("setting up login manager")
        login_manager = LoginManager()
        login_manager.login_view = "session.authorization"

        @login_manager.user_loader
        @context
        def __load_user(ctx: AppContext, user_id):
            return ctx.database.session.query(models.User).get(user_id)

        login_manager.init_app(ctx.app)
        ctx.app.permanent_session_lifetime = timedelta(days=3)
