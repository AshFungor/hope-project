import copy

import flask
import flask_login
import sqlalchemy as orm

from app.models import CityHall, User, Goal
from app.routes import Blueprints
from app.context import function_context, AppContext
from app.routes.queries import CRUD
from app.routes.queries.common import get_last


@Blueprints.accounts.route("/city_hall")
@flask_login.login_required
@function_context
def city_hall(ctx: AppContext):
    current_user = copy.copy(flask_login.current_user)
    hall = ctx.database.session.scalar(orm.select(CityHall))

    bank_account, mayor_id, economic_assistant_id, social_assistant_id = (
        hall.bank_account_id,
        hall.mayor_id,
        hall.economic_assistant_id,
        hall.social_assistant_id,
    )

    names = ctx.database.session.scalars(
        orm
        .select(User)
        .filter(User.id.in_((mayor_id, economic_assistant_id, social_assistant_id)))
    ).all()

    spec = {name.id: name.full_name_string for name in names}
    mayor, economic_assistant, social_assistant = spec[mayor_id], spec[economic_assistant_id], spec[social_assistant_id]
    roles = {
        "mayor": current_user.id == mayor_id,
        "economic_assistant": current_user.id == economic_assistant_id,
        "social_assistant": current_user.id == social_assistant_id,
    }

    goal: Goal = get_last(hall.bank_account_id, True)
    if goal is None and roles["mayor"]:
        return flask.redirect(flask.url_for("goal_view.view_create_goal", account=hall.bank_account_id))
    if goal:
        setattr(goal, "rate", goal.get_rate(CRUD.read_money(hall.bank_account_id)))

    # bankrupt_users, bankrupt_companies, bankrupt_cities = prefecture.query_bankrupts("mayor", None)
    bankrupt_users = bankrupt_companies = bankrupt_cities = []

    return flask.render_template(
        "accounts/city_hall.html",
        balance=CRUD.read_money(bank_account),
        bank_account=bank_account,
        goal=goal,
        mayor=mayor,
        economic_assistant=economic_assistant,
        social_assistant=social_assistant,
        roles=roles,
        bankrupt_users=bankrupt_users,
        bankrupt_companies=bankrupt_companies,
        bankrupt_cities=bankrupt_cities,
    )
