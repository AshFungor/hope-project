import logging
import typing

import flask
import flask_login
import sqlalchemy as orm

import app.models as models
import app.routes.blueprints as blueprints
from app.env import env
from app.forms.new_product import NewProductForm


def visitor(field: any, type: str) -> None | str:
    if type.lower().startswith("name"):
        matches = env.db.impl().session.execute(orm.select(models.Product).filter(models.Product.name == field)).scalars().all()
        if len(matches):
            return f"имя продукта уже существует: {field}"
    if type.lower().startswith("level"):
        if not field.isnumeric():
            return "уровень должен быть числом"
        if not (1 <= int(field) <= 4):
            return "уровень должен быть в промежутке от 1 до 4"
    if type.lower().startswith("category"):
        if field not in ["MINERALS", "ENERGY", "FOOD", "TECHNIC", "CLOTHES"]:
            return f"категория не существует: {field}"


def add_product(name: str, level: int, category: str) -> typing.Tuple[bool, str]:
    # current_user_id = flask_login.current_user.id
    try:
        product = models.Product(category=category, name=name, level=level)
    except ValueError as value_error:
        logging.warning(f"product params validation failed: {value_error}")
        return False, "Ошибка при создании товара"

    try:
        env.db.impl().session.add(product)
        env.db.impl().session.commit()
    except Exception as error:
        logging.warning(f"product insertion failed: {error}")
        return False, "Ошибка при добавлении товара"

    return True, "Товар успешно создан"


@blueprints.master.route("/new_product", methods=["GET", "POST"])
@flask_login.login_required
def create_product():
    """Создание нового продукта (только для нужд мастера игры или администратора)"""
    form = NewProductForm()

    if flask.request.method == "POST" and form.validate_on_submit():

        data = [form.product_name.data, form.level.data, form.category.data]
        for field, type in zip([form.product_name.data, form.level.data, form.category.data], ("name", "level", "category")):
            result = visitor(field, type)
            if result is not None:
                flask.flash(result, category="warning")
                return flask.render_template("main/new_product.html", form=form, products=models.Product.get_all())

        name, level, category = data
        created, message = add_product(name, int(level), category)

        if created:
            flask.flash(message, category="info")
            return flask.redirect(flask.url_for("master.create_product"))
        else:
            flask.flash(message, category="warning")

    return flask.render_template("main/new_product.html", form=form, products=models.Product.get_all())
