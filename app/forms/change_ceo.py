from flask_wtf import FlaskForm
import wtforms as wtf
from wtforms.validators import InputRequired, NumberRange


class ChangeCeoForm(FlaskForm):
    company_id = wtf.IntegerField(
        'Номер банковского счета компании:',
        validators=[
            InputRequired(),
            NumberRange(min=1, message='Должен быть положительным числом')
        ],
        render_kw={'placeholder': 'Введите номер банковского счета компании'}
    )

    new_ceo_id = wtf.IntegerField(
        'Номер банковского счета нового генерального директора:',
        validators=[
            InputRequired(),
            NumberRange(min=1, message='Должен быть положительным числом')
        ],
        render_kw={'placeholder': 'Введите номер банковского счета нового генерального директора'}
    )

    confirm_change = wtf.BooleanField(
        'Подтверждаю смену генерального директора',
        validators=[InputRequired()]
    )

    submit = wtf.SubmitField('Изменить генерального директора')
