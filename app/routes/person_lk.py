import datetime

from flask import Blueprint, render_template, url_for

from app.modules.database.validators import CurrentTimezone
from app.env import env

# models and parsing
import app.models as models
import os, csv, dateutil


person_lk = Blueprint('person_lk', __name__)

@person_lk.route('/person_lk')
def person_cabinet():
    models.User(
        None,
        0,
        'а',
        'а',
        'a',
        'a',
        'female',
        0,
        datetime.datetime.now(CurrentTimezone)
    )
    """Личный кабинет пользователя"""
    return render_template('main/person_lk_page.html')


