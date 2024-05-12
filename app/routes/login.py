from flask import Blueprint, render_template, url_for

login = Blueprint('login', __name__)


@login.route('/login')
def login():
    """Страничка входа"""
    return "Логинка!!!"
