from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class CompanyAccountsForm(FlaskForm):
    # Счета
    company_account = StringField(
        'Счет компании',
        validators=[DataRequired(message="Обязательное поле")],
        render_kw={"class": "form-control text-center", "placeholder": "Введите номер счета компании"}
    )

    ceo_account = StringField(
        'Счет ген. директора',
        validators=[DataRequired(message="Обязательное поле")],
        render_kw={"class": "form-control text-center", "placeholder": "Введите номер счета ген. директора"}
    )

    employee_account = StringField(
        'Счет работника',
        validators=[DataRequired(message="Обязательное поле")],
        render_kw={"class": "form-control text-center", "placeholder": "Введите номер счета работника"}
    )

    # Роли (используем ваш маппер)
    employee_role = SelectField(
        'Роль работника',
        choices=[
            ('', 'Выберите новую роль'),
            ('CEO', 'генеральный директор'),
            ('CFO', 'финансовый директор'),
            ('marketing_manager', 'маркетолог'),
            ('production_manager', 'заведущий производством'),
            ('employee', 'рабочий')
        ],
        validators=[DataRequired(message="Выберите роль")],
        render_kw={"class": "form-select text-center"}
    )

    confirm_change = BooleanField(
        'Подтверждаю смену ролей',
        validators=[DataRequired(message="Требуется подтверждение")],
        render_kw={"class": "form-check-input"}
    )

    submit = SubmitField(
        'Сохранить изменения',
        render_kw={"class": "btn btn-success w-100"}
    )