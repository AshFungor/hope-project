from flask import Blueprint, render_template, url_for
from app.env import env

import models

person_lk = Blueprint('person_lk', __name__)

@person_lk.route('/person_lk')
def person_cabinet():

    # TODO УДАЛИТЬ ПОСЛЕ НАПИСАНИЯ МОДЕЛЕЙ!
    # ПРИМЕР СОЗДАНИЯ ОБЪЕКТА В БД
    
    product = models.Product()
    product.category = 'kek'
    product.level = 0
    product.name = 'azazaza'
    env.db.impl().session.add(product)
    env.db.impl().session.commit()
    """Личный кабинет пользователя"""
    return render_template('main/person_lk_page.html')
