import flask
from flask import Blueprint, render_template, url_for, request
from flask_login import login_required, current_user

import sqlalchemy

from app.env import env
import app.models as models

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints


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
        companies = env.db.impl().session.execute(query_companies).all()
        return render_template('main/companies.html', companies=companies)
    # проверяем, доступно ли управление фирмой текущему пользователю
    query_companies = (
        sqlalchemy.select(
            models.User2Company.company_id
        ).filter(sqlalchemy.and_(models.User2Company.user_id == current_user.id,
                 models.User2Company.company_id == company_id))
    )
    companies = env.db.impl().session.execute(query_companies).all()
    if len(companies) > 0:
        return render_template('main/company.html')
    return flask.Response("Доступ к запрошенной фирме запрещён", status=403)
