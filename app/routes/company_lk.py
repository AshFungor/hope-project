import flask
from flask import Blueprint, render_template, url_for, request
from flask_login import login_required, current_user

import sqlalchemy

from app.env import env
import app.models as models

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints
import app.routes.person_account as account

@blueprints.accounts_blueprint.route('/company_lk')
@login_required
def company_cabinet():
    """Личный кабинет компании"""
    company_id = request.args.get("company_id", None)
    if not company_id:
        # создаём словарь фирм (название: id)
        query_companies = (
            sqlalchemy.select(
                models.User2Company.company_id,
                models.Company.name
            ).join(models.Company, models.User2Company.company_id == models.Company.id)
            .filter(models.User2Company.user_id == current_user.id)
        )
        companies = set(env.db.impl().session.execute(query_companies).all())
        return render_template('main/companies.html', companies=companies)
    # проверяем, доступно ли управление фирмой текущему пользователю
    query_companies = (
        sqlalchemy.select(
            models.User2Company.company_id
        ).filter(sqlalchemy.and_(models.User2Company.user_id == current_user.id,
                 models.User2Company.company_id == company_id))
    )
    company_id = env.db.impl().session.execute(query_companies).scalars().first()
    if company_id:

        query_company = sqlalchemy.select(models.Company).filter(models.Company.id == company_id)
        company = env.db.impl().session.execute(query_company).first()[0]

        goal = models.Goal.get_last(company.bank_account_id, True)
        if goal is None:
            return flask.redirect(flask.url_for('goal_view.view_create_goal', account=company.bank_account_id))
        balance = account.get_money(company.bank_account_id)
        setattr(goal, 'rate', goal.get_rate(balance))

        query_CEO = sqlalchemy.select(models.User).join(
            models.User2Company,
            models.User.id == models.User2Company.user_id
        ).filter(models.User2Company.company_id == company_id,
                 models.User2Company.role == "CEO",
                 models.User2Company.fired_at == None)
        CEO = env.db.impl().session.execute(query_CEO).scalars().first()
        user2company = env.db.impl().session.execute(
            sqlalchemy.select(
                models.User2Company
            )
            .filter(sqlalchemy.and_(
                models.User2Company.user_id == current_user.id,
                models.User2Company.fired_at == None
            ))
        ).scalars().all()
        f_ceo, f_cfo, f_mark, f_prod = False, False, False, False
        for role in user2company:
            if role.role == 'CEO':
                f_ceo = True
            if role.role == 'CFO':
                f_cfo = True
            if role.role == 'marketing_manager':
                f_mark = True
            if role.role == 'production_manager':
                f_prod = True
        return render_template('main/company.html',
                               company=company,
                               CEO=CEO,
                               balance=balance,
                               f_ceo=f_ceo,
                               f_cfo=f_cfo,
                               f_mark=f_mark,
                               f_prod=f_prod,
                               goal=goal)
    return flask.Response("Доступ к запрошенной фирме запрещён", status=403)
