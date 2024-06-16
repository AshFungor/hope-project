from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, NumberRange
import wtforms as wtf


class TransactionForm(FlaskForm):
    bank_account = wtf.IntegerField('Счет получателя',
                                    validators=[InputRequired()])
    amount = wtf.IntegerField('Сумма перевода',
                              validators=[InputRequired(), NumberRange(min=10)])
    submit = wtf.SubmitField('Перевести')
