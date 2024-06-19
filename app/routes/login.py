import flask

from flask import Blueprint, render_template, url_for, session, request, redirect, message_flashed
from flask_login import login_user

from app.env import env
import app.models as models

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints


@blueprints.session_blueprint.route('/login', methods=['POST', 'GET'])
def authorization():
    if request.method == 'POST':
        user = env.db.impl().session.query(models.User).filter_by(
            login=request.form.get('Login')).first()
        if user.password == request.form['Password']:
            login_user(user)
            prefecture = env.db.impl().session.query(models.Prefecture).join(
                models.City, models.Prefecture.id == models.City.prefecture_id).filter(
                models.City.id == user.city_id
            ).first()
            session["prefecture_name"] = prefecture.name
            return redirect(url_for('main.index'))
        else:
            flask.flash('Неверные данные для входа: проверьте введенный логин или пароль')
    return render_template("login/authorization.html")


@blueprints.session_blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('session.authorization'))
