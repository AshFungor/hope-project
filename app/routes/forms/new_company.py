import wtforms as wtf
import sqlalchemy as orm

from flask_wtf import FlaskForm
from wtforms.validators import InputRequired

from app.models import Prefecture
from app.context import function_context, AppContext


class NewCompanyForm(FlaskForm):
    company_name = wtf.StringField("Название фирмы:", validators=[InputRequired()], render_kw={"placeholder": "Название"})
    about = wtf.StringField("Краткое описание компании:", validators=[InputRequired()], render_kw={"placeholder": "Информация о компании"})
    prefecture = wtf.SelectField("Префектура:", choices=[], validators=[InputRequired()])
    founders = wtf.StringField("Учредитель (учредители):", validators=[InputRequired()], render_kw={"placeholder": "Счета через пробел"})
    submit = wtf.SubmitField("Создать компанию")

    @function_context
    def set_choices_prefectures(self, ctx: AppContext):
        self.prefecture.choices = [
            name for name in ctx.database.session.scalars(
                orm.select(Prefecture.name)
            ).all()
        ]
