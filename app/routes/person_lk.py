import datetime

from flask import Blueprint, render_template, url_for

from app.modules.database.validators import CurrentTimezone
from app.env import env

# models and parsing
import models
import os, csv, dateutil


person_lk = Blueprint('person_lk', __name__)

@person_lk.route('/person_lk')
def person_cabinet():
    """Личный кабинет пользователя"""
    return render_template('main/person_lk_page.html')


