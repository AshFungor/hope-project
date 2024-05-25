from flask import Blueprint, render_template, url_for, session

city_hall_lk = Blueprint('city_hall_lk', __name__)


@city_hall_lk.route('/city_hall_lk')
def city_hall_cabinet():
    """Личный кабинет мэрии"""
    return render_template('main/city_hall.html', session=session)
