from http import HTTPStatus
from flask import request, jsonify
from flask_login import login_required

from app.models import Goal
from app.routes import Blueprints
from app.routes.queries import CRUD, wrap_crud_call
from app.context import function_context, AppContext
from app.routes.queries.common import get_last


@Blueprints.goals.route("/api/goals/get_last", methods=["GET"])
@login_required
@function_context
def get_last_goal(ctx: AppContext):
    account = request.args.get("bank_account_id", type=int)
    if account is None:
        return "Missing parameters", HTTPStatus.BAD_REQUEST

    last = get_last(account, current_day_only=True)
    if last is None:
        return "No goal found for today", HTTPStatus.NOT_FOUND

    return jsonify({
        "bank_account_id": last.bank_account_id,
        "created_at": last.created_at.isoformat() if last.created_at else None,
        "value": last.value
    })


@Blueprints.goals.route("/api/goals/create", methods=["POST"])
@login_required
@function_context
def create_goal(ctx: AppContext):
    data = request.get_json()
    if not data:
        return "Missing JSON payload", HTTPStatus.BAD_REQUEST

    try:
        account = int(data.get("bank_account_id", None))
        value = data.get("value", None)
        if value is not None:
            value = int(value)
    except ValueError:
        return "Missing or invalid values", HTTPStatus.BAD_REQUEST

    last = get_last(account, current_day_only=True)
    if last:
        return "Goal already exists for today", HTTPStatus.CONFLICT

    try:
        current_balance = CRUD.read_money(account)
    except RuntimeError as error:
        return f"Internal server error: {error}", HTTPStatus.INTERNAL_SERVER_ERROR

    @wrap_crud_call
    def __create():
        new_goal = Goal(account, value, current_balance)
        ctx.database.session.add(new_goal)
        ctx.database.session.commit()

    __create()
    return "Goal created", HTTPStatus.OK