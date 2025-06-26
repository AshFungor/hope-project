from datetime import timedelta

from flask_login import LoginManager

from app.context import AppConfig, AppContext, class_context
from app.models import User


class FlaskExtensions:
    @classmethod
    def setup(cls, config: AppConfig):
        if config.flask_extensions.csrf:
            cls.__init_csrf()
        if config.flask_extensions.login_manager:
            cls.__init_login_manager()

    @classmethod
    @class_context
    def __init_login_manager(cls, ctx: AppContext):
        ctx.logger.info("setting up login manager")
        login_manager = LoginManager()

        @login_manager.user_loader
        @class_context
        def __load_user(user_id, ctx: AppContext):
            return ctx.database.session.get(User, user_id)

        login_manager.init_app(ctx.app)
        ctx.app.permanent_session_lifetime = timedelta(days=3)
