from flask import Blueprint, render_template, url_for

company_lk = Blueprint('login', __name__)


@company_lk.route('/login')
def login():
    """Страничка входа"""
    return "Логинка!!!"
