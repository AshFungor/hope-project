from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, NumberRange
import wtforms as wtf


class NewProductForm(FlaskForm):
    # категории: FOOD, TECHNIC, CLOTHES (товары), MINERALS (ресурсы), ENERGY (энергия)
    product_name = wtf.StringField('Название товара',
                                   validators=[InputRequired()])
    category = wtf.SelectField('Вид/категория товара',
                               choices=['MINERALS', 'ENERGY', 'FOOD', 'TECHNIC', 'CLOTHES'],
                               validators=[InputRequired()])
    level = wtf.SelectField('Уровень', choices=['1', '2', '3', '4'], validators=[InputRequired()])
    submit = wtf.SubmitField('Создать товар')
