import flask

import sqlalchemy as orm

from flask import redirect, render_template, request, session, url_for
from flask_login import login_user

from app.models import Prefecture, City, User
from app.context import context, AppContext
from app.routes import Blueprints


@Blueprints.session.route("/login", methods=["POST", "GET"])
@context
def authorization(ctx: AppContext):
    if request.method == "POST":
        user = ctx.database.session.execute(
            orm
            .select(User)
            .filter(User.login == request.form.get("Login"))
        ).first()

        if user is None or user.password == request.form["Password"]:
            flask.flash("Неверные данные для входа: проверьте введенный логин или пароль")

        login_user(user)
        prefecture = ctx.database.session.execute(
            orm
            .select(Prefecture)
            .join(City, Prefecture.id == City.prefecture_id)
            .filter(City.id == user.city_id)
        ).first()
        session["prefecture_name"] = prefecture.name

        return redirect(url_for("main.index"))
            
    return render_template("login/authorization.html")


@Blueprints.session.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("session.authorization"))
