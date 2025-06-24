import wtforms as wtf

from flask_wtf import FlaskForm
from wtforms.validators import InputRequired


class EmploymentForm(FlaskForm):
    bank_account_id = wtf.StringField("Номер банковского счёта", validators=[InputRequired()])
    role = wtf.SelectField(
        "Должность",
        choices=[
            "генеральный директор",
            "финансовый директор",
            "маркетолог",
            "заведущий производством",
            "рабочий"
        ],
        validators=[InputRequired()],
    )

    submit = wtf.SubmitField("Принять на работу")
