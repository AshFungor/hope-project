from flask import Blueprint, render_template, url_for, session

company_lk = Blueprint('company_lk', __name__)


@company_lk.route('/company_lk')
def company_cabinet():
    """Личный кабинет компании"""
    return render_template('main/company.html', session=session)
