from datetime import datetime
from pathlib import Path

import pytest
from flask import Blueprint, Flask
from flask_login import login_user

from app.context import AppContext
from app.extensions import FlaskExtensions
from app.models import BankAccount, User, Sex


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
        # Check if user already exists
        existing_user = ctx.database.session.get(User, user_id)
        if existing_user:
            return existing_user.id
        
        # Check if bank account already exists
        existing_account = ctx.database.session.get(BankAccount, user_id)
        if not existing_account:
            account = BankAccount(id=user_id)
            ctx.database.session.add(account)
        
        user = User(
            bank_account_id=user_id,
            prefecture_id=None,
            name=str(user_id),
            last_name=str(user_id),
            patronymic=str(user_id),
            login=login,
            password="",
            sex=Sex.MALE,
            bonus=0,
            birthday=datetime.now(),
            is_admin=is_admin,
        )

        ctx.database.session.add(user)
        ctx.database.session.commit()

        return user.id


def login_client(client, user_id: int):
    with client.session_transaction() as session:
        session['_user_id'] = str(user_id)
        session['_fresh'] = True
    return user_id


@pytest.fixture(scope="function")
def logged_in_admin(client):
    user_id = create_user(user_id=1, login="admin", is_admin=True)
    return login_client(client, user_id)


@pytest.fixture(scope="function")
def logged_in_normal(client):
    user_id = create_user(user_id=2, login="normal", is_admin=False)
    return login_client(client, user_id)
