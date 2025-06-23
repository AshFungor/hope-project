from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, NumberRange, Length, Regexp
import wtforms as wtf


class EmploymentForm(FlaskForm):
    # должности: ['CEO', 'CFO', 'founder', 'marketing_manager', 'production_manager', 'employee']
    bank_account_id = wtf.StringField('Номер банковского счёта',
                                      validators=[
                                          InputRequired(message="Обязательное поле"),
                                          Length(min=1, max=9,
                                                 message="Номер счёта должен быть от 10 до 20 символов"),
                                          Regexp('^[0-9]+$', message="Только цифры разрешены")
                                      ])
    role = wtf.SelectField('Должность',
                           choices=['генеральный директор', 'финансовый директор', 'маркетолог', 'заведущий производством', 'рабочий'],
                           validators=[InputRequired(message="Выберите должность")])
    submit = wtf.SubmitField('Принять на работу')
