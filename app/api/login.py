import sqlalchemy as orm
from flask import session
from flask_login import current_user, login_required, login_user, logout_user

from app.api import Blueprints
from app.api.helpers import protobufify, pythonify
from app.codegen.hope import Response as Response
from app.codegen.session import (
    LoginRequest,
    LoginResponse,
    LoginResponseLoginStatus,
    LogoutRequest,
    LogoutResponse,
)
from app.codegen.user import (
    UserRequest,
    UserResponse,
    PartialUserRequest,
    PartialUserResponse,
)
from app.codegen.types import User as UserProto
from app.codegen.types import PartialUser as PartialUserProto
from app.context import AppContext
from app.models import Prefecture, User


@Blueprints.session.route("/api/session/login", methods=["POST"])
@pythonify(LoginRequest)
def login(ctx: AppContext, req: LoginRequest):
    user = ctx.database.session.scalar(
        orm.select(User).filter(User.login == req.login)
    )

    if user is None or user.password != req.password:
        login_resp = LoginResponse(status=LoginResponseLoginStatus.UNAUTHORIZED)
        return protobufify(Response(login=login_resp))

    login_user(user)

    if user.prefecture_id is not None:
        prefecture_name = ctx.database.session.get(Prefecture, user.prefecture_id).name
    else:
        prefecture_name = ""

    session["prefecture_name"] = prefecture_name

    return protobufify(
        Response(
            login=LoginResponse(status=LoginResponseLoginStatus.OK)
        )
    )


@Blueprints.session.route("/api/session/logout", methods=["POST"])
@pythonify(LogoutRequest)
def logout(__ctx: AppContext, __req: LogoutRequest):
    logout_user()
    return protobufify(Response(logout=LogoutResponse()))


@Blueprints.session.route("/api/user/current_user", methods=["POST"])
@login_required
@pythonify(UserRequest)
def get_current_user(ctx: AppContext, __req: UserRequest):
    prefecture_name = session.get("prefecture_name", "")
    user_resp = UserResponse(
        user=UserProto(
            name=current_user.name,
            last_name=current_user.last_name,
            patronymic=current_user.patronymic,
            login=current_user.login,
            sex=current_user.sex,
            bonus=current_user.bonus,
            birthday=current_user.birthday.isoformat(),
            bank_account_id=current_user.bank_account_id,
            prefecture_name=prefecture_name,
            is_admin=current_user.is_admin,
        )
    )
    return protobufify(Response(full_user=user_resp))


@Blueprints.session.route("/api/user/partial_user", methods=["POST"])
@login_required
@pythonify(PartialUserRequest)
def get_partial_user(ctx: AppContext, req: PartialUserRequest):
    user = ctx.database.session.scalar(
        orm.select(User).filter(User.bank_account_id == req.bank_account_id)
    )

    if user is None:
        ctx.logger.warning(f"could not get user: {req.bank_account_id} is unknown")
        return protobufify(Response(partial_user=PartialUserResponse()))

    partial_resp = PartialUserResponse(
        user=PartialUserProto(
            name=user.name,
            last_name=user.last_name,
            patronymic=user.patronymic,
            bank_account_id=user.bank_account_id,
        )
    )
    return protobufify(Response(partial_user=partial_resp))
