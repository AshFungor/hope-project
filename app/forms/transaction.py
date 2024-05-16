from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, NumberRange, Length
import wtforms as wtf


class TransactionForm(FlaskForm):
    bank_account = wtf.IntegerField('Счет получателя',
                                    validators=[InputRequired()])
    amount = wtf.IntegerField('Сумма перевода',
                              validators=[InputRequired(), NumberRange(min=10)])
    comment = wtf.StringField('Комментарий',
                              validators=[Length(max=50, message='Превышен максимальный размер сообщения (50 символов)')])
    submit = wtf.SubmitField('Перевести')