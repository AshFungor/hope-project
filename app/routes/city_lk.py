from flask import Blueprint, render_template, url_for

city_lk = Blueprint('city_lk', __name__)


@city_lk.route('/city_lk')
def city_cabinet():
    """Личный кабинет города!!"""
    return render_template('main/city_lk_page.html')
