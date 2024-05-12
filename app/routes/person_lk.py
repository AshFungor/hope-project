from flask import Blueprint, render_template, url_for
from ..extensions import db
from ..models.user import User

person_lk = Blueprint('person_lk', __name__)

@person_lk.route('/person_lk')
def person_cabinet():

    # TODO УДАЛИТЬ ПОСЛЕ НАПИСАНИЯ МОДЕЛЕЙ!
    # ПРИМЕР СОЗДАНИЯ ОБЪЕКТА В БД

    user = User(name="test")
    db.session.add(user)
    db.session.commit()
    """Личный кабинет пользователя"""
    return user.name
