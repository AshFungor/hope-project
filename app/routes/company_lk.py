from flask import Blueprint, render_template, url_for
from flask_login import login_required

company_lk = Blueprint('company_lk', __name__)


@company_lk.route('/company_lk')
# @login_required
def company_cabinet():
    """Личный кабинет компании"""
    return render_template('main/company.html')
