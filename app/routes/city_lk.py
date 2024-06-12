from flask import Blueprint, render_template, url_for
from flask_login import login_required

from app.env import env
import app.models as models

city_lk = Blueprint('city_lk', __name__)


@city_lk.route('/city_lk')
@login_required
def city_cabinet():
    """Личный кабинет города!!"""
    prefecture_mayor = env.db.impl().session.query(
        models.City
    ).join(
        models.User, models.User.id == models.City.mayor_id
    )
    return render_template('main/city_lk_page.html')
