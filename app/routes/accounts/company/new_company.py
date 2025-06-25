import flask
import flask_login
import numpy as np

import sqlalchemy as orm

from flask_login import current_user, login_required
from typing import Optional, Tuple, List
from flask import redirect, render_template, request, url_for

from app.models import Company, Prefecture, User
from app.routes.forms import NewCompanyForm
from app.context import function_context, AppContext
from app.routes.queries import CRUD
from app.routes import Blueprints


@function_context
def make_company(
    ctx: AppContext, name: str, about: str, prefecture_name: str, user_id: int
) -> Optional[Company]:
    prefecture = ctx.database.session.scalar(orm.select(Prefecture).filter(Prefecture.name == prefecture_name))
    if not prefecture:
        ctx.logger.warning(f"user: {user_id}: create company failed: prefecture {prefecture_name} not found")
        return

    bank_account = CRUD.create_bank_account()
    return Company(bank_account, prefecture.id, name, about)


@function_context
def add_company(
    ctx: AppContext, name: str, about: str, founders: List[int], prefecture_name: str
) -> Tuple[bool, str]:
    current_user_id = flask_login.current_user.id

    companies = ctx.database.session.scalars(
        orm
        .select(Company)
        .filter(Company.name == name)
    ).all()

    if len(companies) > 0:
        return False, "Фирма с таким названием уже существует."

    company = make_company(name, about, prefecture_name, current_user)

    if np.unique(founders).shape[0] != len(founders):
        ctx.logger.warning(f"user: {current_user_id} create company failed: not unique founders")
        return False, "Указаны не уникальные учредители"

    ids = ctx.database.session.scalars(
        orm
        .select(User.id)
        .filter(User.bank_account_id.in_(founders))
    ).all()

    if len(ids) < len(founders):
        ctx.logger.warning(f"user: {current_user_id} Failed to match user ids against database records")
        return False, "Указанного учредителя не существует "

    ratios = np.ceil(np.ones(len(founders)) * (1 / len(founders)) * 100)
    ratios[-1] += 100 - np.sum(ratios)

    CRUD.create_company(company, zip(ids, ratios))
    return True, "Фирма успешно создана"


@Blueprints.accounts.route("/master/create/company", methods=["GET", "POST"])
@login_required
@function_context
def create_company(ctx: AppContext):
    form = NewCompanyForm()
    form.set_choices_prefectures()

    if request.method == "POST" and form.validate_on_submit():
        name = form.company_name.data
        description = form.about.data
        founders = list(map(int, form.founders.data.strip().split()))
        prefecture_name = form.prefecture.data
        created, message = add_company(name, description, founders, prefecture_name)

        if created:
            flask.flash(message, category="info")
            return redirect(url_for("accounts.create_company"))
        else:
            flask.flash(message, category="warning")

    return render_template("accounts/master/new_company.html", form=form)
