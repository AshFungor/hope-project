import flask
from flask import Blueprint, render_template, url_for, session, request, redirect, message_flashed
from flask_login import login_user

from app.env import env
import app.models as models

login = Blueprint('login', __name__)


@login.route('/login', methods=['POST', 'GET'])
def authorization():

    """Страничка хода"""

    if request.method == 'POST':
        user = env.db.impl().session.query(models.User).filter_by(
            login=request.form.get('Login')).first()
        if not user:
            flask.flash('Пользователя с таким логином не существует')
        elif user.password == request.form['Password']:
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flask.flash('Неверный пароль')
    return render_template("login/authorization.html")


@login.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))
