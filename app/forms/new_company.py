from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, NumberRange
import wtforms as wtf

from app.env import env
import app.models as models


class NewCompanyForm(FlaskForm):
    company_name = wtf.StringField('Название фирмы:', validators=[InputRequired()], render_kw={'placeholder': 'Название'})
    about = wtf.StringField('Краткое описание компании:', validators=[InputRequired()], render_kw={'placeholder': 'Информация о компании'})
    prefecture = wtf.SelectField('Префектура:', choices=[], validators=[InputRequired()])
    founders = wtf.StringField('Учредитель (учредители):', validators=[InputRequired()], render_kw={'placeholder': 'Счета через пробел'})
    submit = wtf.SubmitField('Создать компанию')

    def set_choices_prefectures(self):
        self.prefecture.choices = [i[0] for i in env.db.impl().session.query(models.Prefecture.name).filter(models.Prefecture.name != 'Штаб').all()]
