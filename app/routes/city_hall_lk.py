import copy

import flask
import flask_login
import sqlalchemy as orm

import app.models as models
import app.modules.database.static as static
import app.routes.blueprints as blueprints
import app.routes.person_account as account
import app.routes.prefecture_lk as prefecture

# local
from app.env import env


@blueprints.accounts_blueprint.route("/city_hall_lk")
@flask_login.login_required
def city_hall_cabinet():
    current_user = copy.deepcopy(flask_login.current_user)
    hall = env.db.impl().session.scalars(orm.select(models.CityHall)).first()

    bank_account, mayor_id, economic_assistant_id, social_assistant_id = (
        hall.bank_account_id,
        hall.mayor_id,
        hall.economic_assistant_id,
        hall.social_assistant_id,
    )

    names = (
        env.db.impl()
        .session.scalars(orm.select(models.User).filter(models.User.id.in_((mayor_id, economic_assistant_id, social_assistant_id))))
        .all()
    )

    spec = {name.id: name.full_name_string for name in names}
    mayor, economic_assistant, social_assistant = spec[mayor_id], spec[economic_assistant_id], spec[social_assistant_id]
    roles = {
        "mayor": current_user.id == mayor_id,
        "economic_assistant": current_user.id == economic_assistant_id,
        "social_assistant": current_user.id == social_assistant_id,
    }

    goal = models.Goal.get_last(hall.bank_account_id, True)
    if goal is None and roles["mayor"]:
        return flask.redirect(flask.url_for("goal_view.view_create_goal", account=hall.bank_account_id))
    if goal:
        setattr(goal, "rate", goal.get_rate(account.get_money(hall.bank_account_id)))

    bankrupt_users, bankrupt_companies, bankrupt_cities = prefecture.query_bankrupts("mayor", None)

    return flask.render_template(
        "main/city_hall.html",
        balance=account.get_money(bank_account),
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
