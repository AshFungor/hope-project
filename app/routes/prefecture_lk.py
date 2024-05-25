from flask import Blueprint, render_template, url_for, session
from app.env import env
from app import models
import datetime
from app.modules.database.static import CurrentTimezone

prefecture_lk = Blueprint('prefecture_lk', __name__)



@prefecture_lk.route('/prefecture_lk')
def prefecture_cabinet():

    """Личный кабинет префектуры"""
    return render_template('main/prefecture_lk_page.html', session=session)
