from flask import Blueprint, render_template, url_for

login = Blueprint('login', __name__)


@login.route('/login')
def authorization():
    """Страничка входа"""
    return render_template("login/authorization.html")
