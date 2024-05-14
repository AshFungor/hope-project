from flask import Blueprint, render_template, url_for
from app.env import env
from app.models.user import User

person_lk = Blueprint('person_lk', __name__)

@person_lk.route('/person_lk')
def person_cabinet():

    # TODO УДАЛИТЬ ПОСЛЕ НАПИСАНИЯ МОДЕЛЕЙ!
    # ПРИМЕР СОЗДАНИЯ ОБЪЕКТА В БД

    user = User(name="test")
    env.db.session.add(user)
    env.db.session.commit()
    """Личный кабинет пользователя"""
    return render_template('main/person_lk_page.html')
