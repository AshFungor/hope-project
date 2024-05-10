from flask import Blueprint, render_template, url_for

master_lk = Blueprint('master_lk', __name__)


@master_lk.route('/master_lk')
def master_cabinet():
    """Личный кабинет мастера"""
    return "Кабинет мастера!!!"
