from flask_wtf import FlaskForm
from wtforms.validators import InputRequired
import wtforms as wtf


class GoalForm(FlaskForm):
    """Форма выбора цели"""

    today_goal = wtf.IntegerField('Цель на сегодня', validators=[InputRequired()])

    submit = wtf.SubmitField('Поставить цель')
