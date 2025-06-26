import sqlalchemy as orm

from flask import session, Response
from flask_login import login_user, logout_user, login_required, current_user

from app.models import Prefecture, User
from app.api.preprocess import preprocess
from app.context import function_context, AppContext
from app.api import Blueprints

from app.codegen.session import (
    LoginRequest,
    LoginResponse,
    LoginResponseLoginStatus,
    UserInfo,
)


@Blueprints.session.route("/api/login", methods=["POST"])
@preprocess(LoginRequest)
@function_context
def login(ctx: AppContext, req: LoginRequest):
    user = ctx.database.session.scalar(
        orm.select(User).filter(User.login == req.login)
    )

    if user is None or user.password != req.password:
        resp = LoginResponse(
            status=LoginResponseLoginStatus.UNAUTHORIZED,
            message="login or password did not match"
        )
        return Response(bytes(resp), content_type="application/protobuf", status=401)

    login_user(user)
    prefecture = ctx.database.session.get(Prefecture, user.prefecture_id)
    prefecture_name = prefecture.name if prefecture is not None else ''

    session["prefecture_name"] = prefecture_name

    resp = LoginResponse(
        status=LoginResponseLoginStatus.OK,
        message=prefecture_name
    )
    return Response(bytes(resp), content_type="application/protobuf", status=200)


@Blueprints.session.route("/api/logout", methods=["POST"])
def logout():
    logout_user()
    resp = LoginResponse(
        status=LoginResponseLoginStatus.OK,
        message="logged out"
    )
    return Response(bytes(resp), content_type="application/protobuf", status=200)


@Blueprints.session.route("/api/current_user", methods=["GET"])
@login_required
@function_context
def get_current_user(ctx: AppContext):
    prefecture_name = session.get("prefecture_name")

    if not prefecture_name:
        prefecture_name = ctx.database.session.scalar(
            orm.select(Prefecture.name).filter(Prefecture.id == current_user.prefecture_id)
        )
        session["prefecture_name"] = prefecture_name

    resp = UserInfo(
        name=current_user.name,
        last_name=current_user.last_name,
        patronymic=current_user.patronymic,
        login=current_user.login,
        sex=current_user.sex,
        bonus=current_user.bonus,
        birthday=current_user.birthday.isoformat(),
        bank_account_id=current_user.bank_account_id,
        prefecture_name=prefecture_name
    )
    return Response(bytes(resp), content_type="application/protobuf", status=200)
