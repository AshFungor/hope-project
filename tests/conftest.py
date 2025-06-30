import pytest

from pathlib import Path
from datetime import datetime
from flask import Flask, Blueprint

from app.context import AppContext
from app.extensions import FlaskExtensions
from app.models import User, BankAccount, Product


@pytest.fixture(scope="session")
def test_app():
    config_path = Path(__file__).parent / "test.yaml"

    app = Flask(__name__)
    ctx = AppContext(app, config_path)
    app.config.update({"TESTING": True})

    from app.api.blueprints import Blueprints
    for bp in vars(Blueprints).values():
        if isinstance(bp, Blueprint):
            app.register_blueprint(bp)

    FlaskExtensions.setup(ctx.config)
    yield app


@pytest.fixture(scope="session")
def client(test_app):
    return test_app.test_client()


def create_user(user_id: int, login: str, is_admin: bool) -> int:
    ctx = AppContext.safe_load()
    with ctx.app.app_context():
        account = BankAccount(id=user_id)
        user = User(
            bank_account_id=user_id,
            prefecture_id=None,
            name=f"Name{user_id}",
            last_name=f"Last{user_id}",
            patronymic=f"Patro{user_id}",
            login=login,
            password="pass",
            sex="male",
            bonus=0,
            birthday=datetime.now(),
            is_admin=is_admin,
        )

        ctx.database.session.add_all([account, user])
        ctx.database.session.commit()

        return user.id


def login_client(client, user_id: int):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
    return client


@pytest.fixture(scope="session")
def logged_in_admin(client):
    user_id = create_user(user_id=1, login='admin', is_admin=True)
    return login_client(client, user_id)


@pytest.fixture(scope="session")
def logged_in_normal(client):
    user_id = create_user(user_id=2, login='normal', is_admin=False)
    return login_client(client, user_id)
