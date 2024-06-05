from flask import Blueprint, render_template, url_for
from flask_login import login_required

master_lk = Blueprint('master_lk', __name__)


@master_lk.route('/master_lk')
@login_required
def master_cabinet():
    """Личный кабинет мастера"""
    return render_template('main/master_lk.html')
