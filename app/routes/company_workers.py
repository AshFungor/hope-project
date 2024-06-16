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
        return redirect(url_for("accounts.company_workers", company_id=company_id))
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
                                 models.User2Company.fired_at == None))
    )
    company_id = env.db.impl().session.execute(query_companies).scalars().first()
    # ещё надо сделать проверку, имеет ли право текущий пользователь работать с сотрудниками
    if company_id:
        query_company = sqlalchemy.select(models.Company).filter(models.Company.id == company_id)
        company = env.db.impl().session.execute(query_company).first()[0]
        # получаем список всех сотрудников текущей фирмы
        query = sqlalchemy.select(
            models.User.name, models.User.last_name, models.User.patronymic,
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
