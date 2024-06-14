import logging
import typing

import flask
import flask_login

from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import login_required, current_user

import app.models as models
from app.env import env

import app.routes.blueprints as blueprints

from app.forms.new_product import NewProductForm


def add_product(name: str, category: str, level: int) -> typing.Tuple[bool, str]:
    # current_user_id = flask_login.current_user.id
    try:
        product = models.Product(
            category=category,
            name=name,
            level=level
        )
    except ValueError as value_error:
        logging.warning(f'product params validation failed: {value_error}')
        return False, "Ошибка при создании товара"

    env.db.impl().session.add(product)
    env.db.impl().session.commit()

    return True, "Товар успешно создан"


@blueprints.accounts_blueprint.route('/new_product', methods=['GET', 'POST'])
@login_required
def create_product():
    """Создание нового продукта (только для нужд мастера игры или администратора) """
    form = NewProductForm()

    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data
        level = form.level.data
        category = form.category.data
        created, message = add_product(name, level, category)

        if created:
            flask.flash(message, category="info")
            return redirect(url_for("new_product.create_product"))
        else:
            flask.flash(message, category="warning")
    return render_template('main/new_product.html', form=form)
