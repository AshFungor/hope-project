from http import HTTPStatus
from flask import Response
from flask_login import login_required

from app.models import Goal
from app.api import Blueprints
from app.api.preprocess import preprocess
from app.models.queries import CRUD, wrap_crud_call
from app.context import function_context, AppContext
from app.models.queries import get_last

from app.codegen.goal import (
	Goal as GoalProto,
	GetLastGoalRequest,
	GoalResponse,
	CreateGoalRequest,
	CreateGoalResponse,
)


@Blueprints.goal.route("/api/goals/get_last", methods=["POST"])
@login_required
@preprocess(GetLastGoalRequest)
@function_context
def get_last_goal(ctx: AppContext, req: GetLastGoalRequest):
	last = get_last(req.bank_account_id, current_day_only=True)
	if last is None:
		return "No goal found for today", HTTPStatus.NOT_FOUND

	resp = GoalResponse(GoalProto(
		last.bank_account_id,
		last.created_at.isoformat() if last.created_at else "",
		last.value
    ))
	return Response(bytes(resp), content_type="application/protobuf")


@Blueprints.goal.route("/api/goals/create", methods=["POST"])
@login_required
@preprocess(CreateGoalRequest)
@function_context
def create_goal(ctx: AppContext, req: CreateGoalRequest):
	last = get_last(req.bank_account_id, current_day_only=True)
	if last:
		resp = CreateGoalResponse(status="Goal already exists for today")
		return Response(resp.serialize(), status=HTTPStatus.CONFLICT, content_type="application/protobuf")

	try:
		current_balance = CRUD.read_money(req.bank_account_id)
	except RuntimeError as error:
		return f"Internal server error: {error}", HTTPStatus.INTERNAL_SERVER_ERROR

	@wrap_crud_call
	def __create():
		new_goal = Goal(req.bank_account_id, req.value, current_balance)
		ctx.database.session.add(new_goal)
		ctx.database.session.commit()

	__create()

	resp = CreateGoalResponse(status="Goal created")
	return Response(bytes(resp), content_type="application/protobuf")
