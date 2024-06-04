from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, NumberRange
import wtforms as wtf


class SuggestionForm(FlaskForm):
    bank_account = wtf.IntegerField('Cчет получателя',
                                    validators=[InputRequired()])
    product = wtf.StringField('Продукт',
                              validators=[InputRequired()])
    count = wtf.IntegerField('Количество',
                             validators=[InputRequired(), NumberRange(min=1)])
    amount = wtf.IntegerField('Стоимость',
                              validators=[InputRequired(), NumberRange(min=1)])
    submit = wtf.SubmitField('Предложить обмен')
