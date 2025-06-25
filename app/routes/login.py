from flask import jsonify

import sqlalchemy as orm

from flask import request, session
from flask_login import login_user, logout_user, login_required, current_user

from app.models import Prefecture, City, User
from app.context import function_context, AppContext
from app.routes import Blueprints


@Blueprints.session.route("/api/login", methods=["POST"])
@function_context
def login(ctx: AppContext):
    data = request.get_json()
    login = data.get("login")
    password = data.get("password")

    user = ctx.database.session.scalar(
        orm.select(User).filter(User.login == login)
    )

    if user is None or user.password != password:
        return jsonify({"error": "Неверный логин или пароль"}), 401

    login_user(user)

    prefecture_name, city_name = ctx.database.session.execute(
        orm.select(Prefecture.name, City.name)
        .join(City, Prefecture.id == City.prefecture_id)
        .filter(City.id == user.city_id)
    ).first()

    session["city_name"] = city_name
    session["prefecture_name"] = prefecture_name

    return jsonify({"message": "ok", "prefecture_name": prefecture_name})


@Blueprints.session.route("/api/logout", methods=["POST"])
def logout():
    logout_user()
    return jsonify({"message": "logged out"})


@Blueprints.session.route("/api/current_user", methods=["GET"])
@login_required
@function_context
def get_current_user(ctx: AppContext):
    prefecture_name = session.get("prefecture_name")
    city_name = session.get("city_name")

    if not prefecture_name:
        prefecture_name = ctx.database.session.scalar(
            orm.select(Prefecture.name)
            .join(City, Prefecture.id == City.prefecture_id)
            .filter(City.id == current_user.city_id)
        )
        session["prefecture_name"] = prefecture_name

    return jsonify({
        "name": current_user.name,
        "bank_account_id": current_user.bank_account_id,
        "last_name": current_user.last_name,
        "patronymic": current_user.patronymic,
        "login": current_user.login,
        "sex": current_user.sex,
        "bonus": current_user.bonus,
        "birthday": current_user.birthday.isoformat(),
        "login": current_user.login,
        "city_name": city_name,
        "prefecture_name": prefecture_name
    })
