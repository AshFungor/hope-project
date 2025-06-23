import wtforms as wtf
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, NumberRange


class EmploymentForm(FlaskForm):
    # должности: ['CEO', 'CFO', 'founder', 'marketing_manager', 'production_manager', 'employee']
    bank_account_id = wtf.StringField("Номер банковского счёта", validators=[InputRequired()])
    role = wtf.SelectField(
        "Должность",
        choices=["генеральный директор", "финансовый директор", "маркетолог", "заведущий производством", "рабочий"],
        validators=[InputRequired()],
    )
    submit = wtf.SubmitField("Принять на работу")
