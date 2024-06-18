from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, NumberRange
import wtforms as wtf


class EmploymentForm(FlaskForm):
    # должности: ['CEO', 'CFO', 'founder', 'marketing_manager', 'production_manager', 'employee']
    bank_account_id = wtf.StringField('Номер банковского счёта',
                                      validators=[InputRequired()])
    role = wtf.SelectField('Должность',
                           choices=['CEO', 'CFO', 'marketing_manager', 'production_manager', 'employee'],
                           validators=[InputRequired()])
    submit = wtf.SubmitField('Принять на работу')
