import flask
import sqlalchemy as orm

from flask import render_template, request
from flask_login import current_user, login_required

from app.routes.queries import CRUD
from app.context import function_context, AppContext
from app.routes.queries.common import get_last
from app.models import User2Company, Company, User, Role, Office
from app.routes import Blueprints


@Blueprints.accounts.route("/company")
@login_required
@function_context
def company(ctx: AppContext):
    company_id = request.args.get("company_id", None)
    if not company_id:
        companies = set(ctx.database.session.execute(
            orm
            .select(User2Company.company_id, Company.name)
            .join(Company, User2Company.company_id == Company.id)
            .filter(User2Company.user_id == current_user.id)
        ).all())
        return render_template("accounts/company/companies.html", companies=companies)

    company_id = ctx.database.session.scalars(
        orm
        .select(User2Company.company_id)
        .filter(
            orm.and_(
                User2Company.user_id == current_user.id,
                User2Company.company_id == company_id
            )
        )
    ).first()

    if company_id:
        company = ctx.database.session.scalar(
            orm
            .select(Company)
            .filter(Company.id == company_id)
        )

        goal = get_last(company.bank_account_id, True)
        if goal is None:
            return flask.redirect(flask.url_for("goals.view_create_goal", account=company.bank_account_id))

        balance = CRUD.read_money(company.bank_account_id)
        setattr(goal, "rate", goal.get_rate(balance))

        CEO = ctx.database.session.scalar(
            orm
            .select(User)
            .join(User2Company, User.id == User2Company.user_id)
            .filter(
                User2Company.company_id == company_id, 
                User2Company.role == Role.CEO,
                User2Company.fired_at == None
            )
        )

        user2company = ctx.database.session.scalars(
            orm.select(User2Company).filter(
                orm.and_(
                    User2Company.user_id == current_user.id,
                    User2Company.fired_at == None
                )
            )
        ).all()

        f_ceo = f_cfo = f_mark = f_prod  = f_found = False
        for role in user2company:
            if role.role == Role.CEO:
                f_ceo = True
            if role.role == Role.CFO:
                f_cfo = True
            if role.role == Role.MARKETING_MANAGER:
                f_mark = True
            if role.role == Role.PRODUCTION_MANAGER:
                f_prod = True
            if role.role == Role.FOUNDER:
                f_found = True

        offices = ctx.database.session.scalars(
            orm
            .select(Office)
            .filter(Office.company_id == company_id)
        ).all()
    
        return render_template(
            "accounts/company/company.html",
            company=company,
            CEO=CEO,
            balance=balance,
            offices=offices,
            f_ceo=f_ceo,
            f_cfo=f_cfo,
            f_mark=f_mark,
            f_prod=f_prod,
            f_found=f_found,
            goal=goal,
        )

    return flask.Response("Доступ к запрошенной фирме запрещён", status=403)
