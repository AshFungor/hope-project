import wtforms as wtf

from flask_wtf import FlaskForm
from wtforms.validators import InputRequired


class NewProductForm(FlaskForm):
    product_name = wtf.StringField("Название товара", validators=[InputRequired()])
    category = wtf.SelectField("Вид/категория товара", choices=["MINERALS", "ENERGY", "FOOD", "TECHNIC", "CLOTHES"], validators=[InputRequired()])
    level = wtf.SelectField("Уровень", choices=["1", "2", "3", "4"], validators=[InputRequired()])
    submit = wtf.SubmitField("Создать товар")
