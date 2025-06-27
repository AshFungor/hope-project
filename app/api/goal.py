from flask_login import login_required

from app.api import Blueprints
from app.api.helpers import preprocess, protobufify, local_datetime
from app.codegen.goal import CreateGoalRequest, CreateGoalResponse, GetLastGoalRequest, CreateGoalResponseStatus
from app.codegen.goal import Goal as GoalProto
from app.codegen.goal import GoalResponse
from app.context import AppContext, function_context
from app.models import Goal
from app.models.queries import CRUD, get_last, wrap_crud_context


@Blueprints.goal.route("/api/goals/get_last", methods=["POST"])
@login_required
@preprocess(GetLastGoalRequest)
@function_context
def get_last_goal(ctx: AppContext, req: GetLastGoalRequest):
    last: Goal = get_last(req.bank_account_id, current_day_only=True)
    if last is None:
        return protobufify(
            GoalResponse(None)
        )

    return protobufify(
        GoalResponse(
            GoalProto(
                last.bank_account_id,
                local_datetime(ctx, last.created_at).isoformat(),
                last.value
            )
        )
    )


@Blueprints.goal.route("/api/goals/create", methods=["POST"])
@login_required
@preprocess(CreateGoalRequest)
@function_context
def create_goal(ctx: AppContext, req: CreateGoalRequest):
    last = get_last(req.bank_account_id, current_day_only=True)
    if last:
        return protobufify(
            CreateGoalResponse(
                CreateGoalResponseStatus.ALREADY_EXISTS
            )
        )


    current_balance = CRUD.query_money(req.bank_account_id)

    with wrap_crud_context():
        new_goal = Goal(req.bank_account_id, req.value, current_balance)
        ctx.database.session.add(new_goal)
        ctx.database.session.commit()

    return protobufify(
        CreateGoalResponse(
            CreateGoalResponseStatus.OK
        )
    )
