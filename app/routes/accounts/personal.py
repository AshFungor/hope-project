import copy
import datetime

import flask
import flask_login

from app.routes import Blueprints
from app.routes.queries.common import get_last
from app.routes.queries import CRUD
from app.context import context, AppContext


def time_span_formatter(span: datetime.timedelta) -> str:
    return f"{span.days} дней"


@Blueprints.accounts.route("/personal_account")
@flask_login.login_required
@context
def person_account(ctx: AppContext):
    current_user = copy.copy(flask_login.current_user)
    goal = get_last(current_user.bank_account_id, True)
    if goal is None:
        return flask.redirect(flask.url_for("goal_view.view_create_goal"))

    balance = CRUD.read_money(current_user.bank_account_id)
    setattr(goal, "rate", goal.get_rate(CRUD.read_money(current_user.bank_account_id)))
    setattr(current_user, "money", CRUD.read_money(current_user.bank_account_id))
    setattr(current_user, "full_name", current_user.full_name_string)

    specs = []
    mapper = {
        "bank_account_id": "номер банковского счета",
        "money": "баланс счета",
        "full_name": "полное имя",
        "login": "логин",
        "birthday": "день рождения",
        "bonus": "бонус",
    }

    consumption_data = {}
    # for name in consumption.norms:
    #     status, left = models.Consumption.did_consume_enough(
    #         current_user.bank_account_id, name, consumption.norms[name], consumption.time_accounted[name]
    #     )
    #     consumption_data[name] = {
    #         "Употребление": "да" if status else "нет",
    #         "Норма употребления": consumption.norms[name],
    #         "Эпизодичность": time_span_formatter(consumption.time_accounted[name]),
    #     }

    for spec in mapper:
        specs.append({"name": mapper[spec], "value": getattr(current_user, spec)})
    return flask.render_template("main/person_account_page.html", user_spec=specs, goal=goal, balance=balance, consumption_data=consumption_data)
