import datetime

import flask
from flask import Blueprint, render_template, url_for, request, redirect
from flask_login import login_required, current_user

import sqlalchemy

from app.env import env
import app.models as models

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints
from app.models.helpers import get_bank_account_size
from app.forms.employment import EmploymentForm
from app.modules.database.validators import CurrentTimezone

logger = env.logger.getChild(__name__)


@blueprints.accounts_blueprint.route('/company_worker_employment', methods=['GET', 'POST'])
@login_required
def company_worker_employment():
    """ Нанимаем сотрудника фирмы """
    company_id = request.args.get("company_id", None)
    company_id = request.form.get('company_id', None) if company_id is None else company_id
    company = env.db.impl().session.execute(
        sqlalchemy.select(
            models.Company
        )
        .filter(models.Company.id == company_id)
    ).scalars().first()
    if company is None:
        return flask.Response(f"Не указана компания или компании не существует ({company_id})", status=443)

    form = EmploymentForm()

    if request.method == 'POST' and form.validate_on_submit():
        mapper = {
            'генеральный директор': 'CEO',
            'финансовый директор': 'CFO',
            'маркетолог': 'marketing_manager',
            'заведущий производством': 'production_manager',
            'рабочий': 'employee'
        }
        worker_bank_account_id = form.bank_account_id.data
        role = mapper.get(str(form.role.data), None)

        # проверяем
        query_user = sqlalchemy.select(models.User).filter(
            models.User.bank_account_id == worker_bank_account_id)
        user = env.db.impl().session.execute(query_user).first()
        if not user:
            flask.flash('Указан неверный банковский счёт пользователя', category="warning")
            logger.error('Incorrect user bank_id during employment.')
            return redirect(url_for("accounts.company_cabinet", company_id=company_id))
        user = user[0]

        # принимаем на работу
        env.db.impl().session.add(models.User2Company(
            user_id=user.id,
            company_id=int(company_id),
            role=role,
            ratio=0,
            employed_at=datetime.datetime.now(tz=CurrentTimezone)
        ))
        env.db.impl().session.commit()
        flask.flash('Пользователь трудоустроен', category="info")
        return redirect(url_for("accounts.company_cabinet", company_id=company_id))
    return render_template('main/company_workers_employment.html', company_id=company_id, company=company, form=form)


@blueprints.accounts_blueprint.route('/company_worker_fire')
@login_required
def company_worker_fire():
    """ Увольняем сотрудника фирмы """
    company_id = request.args.get("company_id", None)
    user_id = request.args.get("user_id", None)
    user_role = request.args.get("user_role", None)
    if not company_id or not user_id:
        return flask.Response("Не указана компания и/или сотрудник", status=404)
    # проверяем, доступно ли управление фирмой текущему пользователю
    query_companies = (
        sqlalchemy.select(
            models.User2Company.company_id
        ).filter(sqlalchemy.and_(models.User2Company.user_id == current_user.id,
                                 models.User2Company.company_id == company_id))
    )
    company_id = env.db.impl().session.execute(query_companies).scalars().first()
    # ещё надо сделать проверку, имеет ли право текущий пользователь работать с сотрудниками
    if company_id:
        worker_query = (sqlalchemy.select(models.User2Company).
                        filter(sqlalchemy.and_(models.User2Company.user_id == user_id,
                                               models.User2Company.company_id == company_id,
                                               models.User2Company.role == user_role)))
        worker = env.db.impl().session.execute(worker_query).scalars().first()
        worker.fired_at = datetime.datetime.now(env.default_timezone)
        env.db.impl().session.commit()
        return redirect(url_for("accounts.company_cabinet", company_id=company_id))
    return flask.Response("Доступ к увольнению в запрошенной фирме запрещён", status=403)


@blueprints.accounts_blueprint.route('/company_workers')
@login_required
def company_workers():
    """ Кабинет для работы с сотрудниками фирмы """
    company_id = request.args.get("company_id", None)
    if not company_id:
        return flask.Response("Не указана компания", status=404)
    # проверяем, доступно ли управление фирмой текущему пользователю
    query_companies = (
        sqlalchemy.select(
            models.User2Company.company_id
        ).filter(sqlalchemy.and_(models.User2Company.user_id == current_user.id,
                                 models.User2Company.company_id == company_id,
                                 models.User2Company.fired_at == None,
                                 sqlalchemy.or_(models.User2Company.role == 'CEO',
                                                models.User2Company.role == 'founder'),
                                 ))
    )
    company_id = env.db.impl().session.execute(query_companies).scalars().first()
    # ещё надо сделать проверку, имеет ли право текущий пользователь работать с сотрудниками
    if company_id:
        query_company = sqlalchemy.select(models.Company).filter(models.Company.id == company_id)
        company = env.db.impl().session.execute(query_company).first()[0]
        # получаем список всех сотрудников текущей фирмы
        query = sqlalchemy.select(
            models.User.name, models.User.last_name, models.User.patronymic,
            models.User.bank_account_id,
            models.User.id,
            models.User2Company.role
        ).join(
            models.User2Company,
            models.User.id == models.User2Company.user_id
        ).filter(sqlalchemy.and_(
            models.User2Company.company_id == company_id, models.User2Company.fired_at == None
        ))
        # roles = ['CEO', 'CFO', 'founder', 'marketing_manager', 'production_manager', 'employee']
        workers = env.db.impl().session.execute(query).all()
        workers_dict = {}
        for worker in workers:
            workers_dict[worker.role] = workers_dict.get(worker.role, []) + [worker]
        return render_template('main/company_workers.html', company=company, workers=workers_dict)
    return flask.Response("Доступ к запрошенной фирме запрещён", status=403)
