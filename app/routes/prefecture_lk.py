from flask import Blueprint, render_template, url_for

prefecture_lk = Blueprint('prefecture_lk', __name__)


@prefecture_lk.route('/prefecture_lk')
def prefecture_cabinet():
    """Личный кабинет префектуры"""
    return "Кабинет префектуры!!!"
