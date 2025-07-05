from pathlib import Path

import pytest
from flask import Blueprint, Flask

from app.codegen.hope import Request, Response
from app.codegen.session import LoginRequest, LoginResponseLoginStatus
from app.context import AppContext
from app.extensions import FlaskExtensions


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


def login_client(client, login: str, password: str = ""):
    request = LoginRequest(login=login, password=password)

    response = client.post(
        "/api/session/login",
        data=bytes(Request(login=request)),
        content_type="application/protobuf",
    )

    assert response.status_code == 200, f"Login failed: {response.data}"
    response = Response().parse(response.data).login
    assert response.status == LoginResponseLoginStatus.OK, f"Login not OK: {login}"


@pytest.fixture(scope="module")
def logged_in_admin(client):
    from tests.helpers.orm import TestCRUD

    ctx = AppContext.safe_load()
    login, password = "admin", "password"
    with ctx.app.app_context():
        TestCRUD.create_user(login=login, password=password)
        login_client(client, login, password)

        yield

        ctx.database.session.execute(orm.delete(User))


@pytest.fixture(scope="module")
def logged_in_normal(client):
    from tests.helpers.orm import TestCRUD

    login, password = "user", "password"
    with AppContext.safe_load().app.app_context():
        TestCRUD.create_user(login=login, password=password)
        login_client(client, login, password)

        yield

        ctx.database.session.execute(orm.delete(User))
