import sqlalchemy as orm

from flask import Response, session
from flask_login import current_user, login_required, login_user, logout_user

from app.api import Blueprints
from app.api.helpers import preprocess, protobufify
from app.codegen.session import (
    LoginRequest,
    LoginResponse,
    LoginResponseLoginStatus,
    UserInfo,
)
from app.context import AppContext, function_context
from app.models import Prefecture, User


@Blueprints.session.route("/api/login", methods=["POST"])
@preprocess(LoginRequest)
@function_context
def login(ctx: AppContext, req: LoginRequest):
    user = ctx.database.session.scalar(orm.select(User).filter(User.login == req.login))

    if user is None or user.password != req.password:
        resp = LoginResponse(status=LoginResponseLoginStatus.UNAUTHORIZED, message="login or password did not match")
        return Response(bytes(resp), content_type="application/protobuf", status=401)

    login_user(user)
    if user.prefecture_id is not None:
        prefecture_name = ctx.database.session.get(Prefecture, user.prefecture_id).name
    else:
        prefecture_name = ""

    session["prefecture_name"] = prefecture_name

    resp = LoginResponse(status=LoginResponseLoginStatus.OK, message=prefecture_name)
    return protobufify(resp)


@Blueprints.session.route("/api/logout", methods=["POST"])
def logout():
    logout_user()
    resp = LoginResponse(status=LoginResponseLoginStatus.OK, message="logged out")
    return protobufify(resp)


@Blueprints.session.route("/api/current_user", methods=["GET"])
@login_required
def get_current_user():
    prefecture_name = session.get("prefecture_name")

    return protobufify(UserInfo(
        name=current_user.name,
        last_name=current_user.last_name,
        patronymic=current_user.patronymic,
        login=current_user.login,
        sex=current_user.sex,
        bonus=current_user.bonus,
        birthday=current_user.birthday.isoformat(),
        bank_account_id=current_user.bank_account_id,
        prefecture_name=prefecture_name,
    ))
