from flask import Blueprint, render_template, url_for

person_lk = Blueprint('person_lk', __name__)


@person_lk.route('/person_lk')
def person_cabinet():
    """Личный кабинет пользователя"""
    return render_template('main/person_lk_page.html')
