from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, NumberRange
import wtforms as wtf

from app.env import env
import app.models as models


class SwitchPrefectureForm(FlaskForm):
    company_bank_account = wtf.IntegerField(
        'Счет фирмы:',
        validators=[
            InputRequired(),
            NumberRange(min=1, message='Должно быть положительное число')
        ],
        render_kw={'placeholder': 'Введите счет фирмы'}
    )

    new_prefecture_name = wtf.SelectField(
        'Новая префектура:',
        choices=[],
        validators=[InputRequired()]
    )

    submit = wtf.SubmitField('Сменить префектуру')

    def set_choices_prefectures(self):
        self.new_prefecture_name.choices = [
            (i[0], i[0]) for i in env.db.impl().session.query(models.Prefecture.name).filter(models.Prefecture.name != 'Штаб').all()
        ]
