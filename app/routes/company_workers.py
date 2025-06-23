import datetime

import flask
from flask import Blueprint, render_template, url_for, request, redirect
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy

import sqlalchemy

from app.env import env
from app.models.company import CompanyAction
import app.models as models

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints
from app.models.helpers import get_bank_account_size
from app.forms.employment import EmploymentForm
from app.modules.database.validators import CurrentTimezone

logger = env.logger.getChild(__name__)


def check_free(role: str, company_id: str, user_id: int) -> bool:
    role = env.db.impl().session.execute(
        sqlalchemy.select(
            models.User2Company.role
        ).filter(
            sqlalchemy.and_(
                sqlalchemy.or_(
                    models.User2Company.role == role,
                    models.User2Company.user_id == user_id,
                ),
                models.User2Company.fired_at == sqlalchemy.null(),
                models.User2Company.company_id == company_id,
            )
        )
    ).scalars().first()
    return role is None


def not_employee(company_id: str, user_id: int):
    role = env.db.impl().session.execute(
        sqlalchemy.select(
            models.User2Company.role
        ).filter(
            sqlalchemy.and_(
                models.User2Company.company_id == company_id,
                models.User2Company.user_id == user_id,
                models.User2Company.role == 'employee'
            )
        )
    ).scalars().first()
    return role is None


def info_generation(user_id: int, role: str, role_free: bool) -> (str, str, str):
    fail_pattern = f"user_id: {current_user.id}. hiring validation failed"
    if not user_id:
        return (
            "Пользователь с указанным счетом не найден. Проверьте данные и попробуйте еще раз.",
            f"{fail_pattern}: user for work not found",
            "warning"
        )
    elif not role:
        return (
            f"Указанная роль ({role}) недопустима.",
            f"{fail_pattern}: incorrect worker role.",
            "warning"
        )
    elif not role_free:
        return (
            "Эта роль уже занята. Выберите другую или освободите текущую.",
            f"{fail_pattern}: role is inaccessible.",
            "warning"
        )
    return (
        "Пользователь трудоустроен",
        f"user_id: {current_user.id}. hiring the user successfully completed",
        "info"
    )


def set_worker(role: str, company_id: str, worker_account_id: int) -> (str, str, str):

    """ Проверяем условия найма на работу """
    query_user_id = (sqlalchemy.select(models.User.id)
                               .filter(models.User.bank_account_id == worker_account_id))
    user_id = env.db.impl().session.execute(query_user_id).scalars().first()
    role_is_free = (check_free(role, company_id, user_id) if role != 'employee'
                    else not_employee(company_id, user_id))
    if all((user_id, role, role_is_free)):
        env.db.impl().session.add(models.User2Company(
            user_id=user_id,
            company_id=int(company_id),
            role=role,
            ratio=0,
            employed_at=datetime.datetime.now(tz=CurrentTimezone)
        ))
        env.db.impl().session.commit()
    return info_generation(user_id, role, role_is_free)


@blueprints.accounts_blueprint.route('/company_worker_employment', methods=['GET', 'POST'])
@login_required
def company_worker_employment():
    form = EmploymentForm()

    company_id = request.args.get("company_id")
    company_id = request.form.get('company_id') if company_id is None else company_id

    query_company = sqlalchemy.select(models.Company).filter(models.Company.id == company_id)
    db: SQLAlchemy = env.db.impl()
    company = db.session.execute(query_company).one()

    """ Проверяем, есть ли права на найм каких-либо сотрудников в компании """
    view_rights = models.company.companyActionPolicy.check_rights(
        user_id=current_user.id,
        company_id=company_id,
        action=models.company.CompanyAction.WORKING_WITH_EMPLOYEES,
    )
    if not view_rights:
        return flask.Response("Доступ к найму в данной фирме запрещен", 403)

    if request.method == 'POST' and form.validate_on_submit():
        """ Проверяем права на найм на конкретную роль """
        role_mapper = {
            'генеральный директор': 'CEO',
            'финансовый директор': 'CFO',
            'маркетолог': 'marketing_manager',
            'заведущий производством': 'production_manager',
            'рабочий': 'employee'
        }
        role = role_mapper[form.role.data]
        hiring_rights = models.company.companyActionPolicy.check_rights(
            user_id=current_user.id,
            company_id=company_id,
            action=models.company.CompanyAction.HIRING,
            hire_role=role
        )
        if hiring_rights:
            """ Нанимаем сотрудника фирмы"""
            mess, log, category = set_worker(role, company_id, int(form.bank_account_id.data))
            flask.flash(mess, category=category)
            logger.info(log) if category == 'info' else logger.error(log)
        else:
            return flask.Response(f"Доступ к найму {form.role.data} в данной фирме запрещен.", 403)
    return render_template(
        'main/company_workers_employment.html',
        company=company,
        company_id=company_id,
        form=form
    )


@blueprints.accounts_blueprint.route('/company_worker_fire')
@login_required
def company_worker_fire():
    """ Увольняем сотрудника фирмы """
    company_id = request.args.get("company_id", None)
    user_id = request.args.get("user_id", None)
    user_role = request.args.get("user_role", None)
    if not company_id or not user_id:
        return flask.Response("Не указана компания и/или сотрудник", status=404)

    rights = models.company.companyActionPolicy.check_rights(
        user_id=current_user.id,
        company_id=company_id,
        action=CompanyAction.HIRING,
        hire_role=user_role
    )
    if rights:
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
    rights = models.company.companyActionPolicy.check_rights(
        user_id=current_user.id,
        company_id=company_id,
        action=models.company.CompanyAction.WORKING_WITH_EMPLOYEES
    )
    if rights:
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
