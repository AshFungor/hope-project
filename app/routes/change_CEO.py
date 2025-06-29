from datetime import datetime
import pytz
import flask
import flask_login
import sqlalchemy

from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import login_required, current_user

import app.models as models
from app.env import env
from app.forms.change_ceo import CompanyAccountsForm

import app.routes.blueprints as blueprints


@blueprints.accounts_blueprint.route('change_ceo_view', method=['GET', 'POST'])
def change_ceo():
    form = CompanyAccountsForm()

    if request.method == 'POST' and form.validate_on_submit():
        company_id = form.company_account.data
        worker_bank_account = form.employee_account.data
        ceo_bank_account = form.ceo_account.data
        role = form.employee_role.data

        # Получаем пользователей из базы
        worker = env.db.impl().session().execute(
            sqlalchemy.select(models.User).filter_by(bank_account_id=worker_bank_account)
        ).scalar_one_or_none()

        ceo = env.db.impl().session().execute(
            sqlalchemy.select(models.User).filter_by(bank_account_id=ceo_bank_account)
        ).scalar_one_or_none()

        if worker is None or ceo is None:
            return flask.Response("Пользователя с таким банковским счетом не существует.", status=404)

        # Проверяем наличие CEO в компании
        ceo_in_company = env.db.impl().session().execute(
            sqlalchemy.select(models.User2Company).filter_by(
                user_id=ceo.id,
                company_id=company_id,
                role='CEO'
            )
        ).scalar_one_or_none()

        # Если CEO нет в компании - регистрируем его
        if ceo_in_company is None:
            new_ceo = models.User2Company(
                user_id=ceo.id,
                company_id=company_id,
                role='CEO',
                ratio=0,
                employed_at=datetime.now(pytz.timezone('Europe/Moscow'))
            )
            env.db.impl().session().add(new_ceo)
            try:
                env.db.impl().session().commit()
            except Exception as ex:
                return flask.Response(f'Ошибка при регистрации CEO: {ex}', status=500)

            ceo_in_company = new_ceo

        # Проверяем наличие работника в компании
        worker_in_company = env.db.impl().session().execute(
            sqlalchemy.select(models.User2Company).filter_by(
                user_id=worker.id,
                company_id=company_id
            )
        ).scalar_one_or_none()

        if worker_in_company is None:
            return flask.Response(f"Работник с таким счетом не существует в данной компании", status=404)

        # Меняем роли
        ceo_in_company.role = role
        worker_in_company.role = 'CEO'

        try:
            env.db.impl().session().commit()
            flask.flash("Роли успешно изменены", category='info')
        except Exception as ex:
            env.db.impl().session().rollback()
            flask.flash("Ошибка при смене ролей", category='warning')
    return render_template('ceo_change.html', form=form)
