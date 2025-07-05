from datetime import timedelta

from flask_login import LoginManager
from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics

from app.context import AppConfig, AppContext, class_context
from app.models import User

metrics = GunicornInternalPrometheusMetrics.for_app_factory()


class FlaskExtensions:
    @classmethod
    def setup(cls, config: AppConfig):
        if config.flask_extensions.csrf:
            cls.__init_csrf()
        if config.flask_extensions.login_manager:
            cls.__init_login_manager()
        if config.flask_extensions.metrics:
            cls.__init_metrics()

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

    @classmethod
    def __init_csrf(cls):
        raise NotImplementedError

    @classmethod
    @class_context
    def __init_metrics(cls, ctx: AppContext):
        ctx.logger.info("setting up flask metrics")
        metrics.init_app(ctx.app)
