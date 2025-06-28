from flask_login import login_required

from app.api import Blueprints
from app.api.helpers import pythonify, protobufify, local_datetime

from app.codegen.goal import CreateGoalRequest, CreateGoalResponse, CreateGoalResponseStatus
from app.codegen.goal import GetLastGoalRequest, GetLastGoalResponse
from app.codegen.types import Goal as GoalProto
from app.codegen.hope import Response

from app.models import Goal
from app.context import AppContext
from app.models.queries import CRUD, get_last, wrap_crud_context


@Blueprints.goal.route("/api/goal/get_last", methods=["POST"])
@login_required
@pythonify(GetLastGoalRequest)
def get_last_goal(ctx: AppContext, req: GetLastGoalRequest):
    last: Goal = get_last(req.bank_account_id, current_day_only=True)
    if last is None:
        return protobufify(Response(
            last_goal=GetLastGoalResponse(goal=None)
        ))

    return protobufify(Response(
        last_goal=GetLastGoalResponse(
            goal=GoalProto(
                bank_account_id=last.bank_account_id,
                value=last.value
            ),
            created_at=local_datetime(ctx, last.created_at).isoformat(),
        ))
    )


@Blueprints.goal.route("/api/goal/create", methods=["POST"])
@login_required
@pythonify(CreateGoalRequest)
def create_goal(ctx: AppContext, req: CreateGoalRequest):
    last = get_last(req.goal.bank_account_id, current_day_only=True)
    if last:
        return protobufify(Response(
            crete_goal=CreateGoalResponse(
                status=CreateGoalResponseStatus.EXISTS
            )
        ))

    current_balance = CRUD.query_money(req.goal.bank_account_id)

    with wrap_crud_context():
        new_goal = Goal(req.goal.bank_account_id, req.goal.value, current_balance)
        ctx.database.session.add(new_goal)
        ctx.database.session.commit()

    return protobufify(Response(
        crete_goal=CreateGoalResponse(
            status=CreateGoalResponseStatus.OK
        )
    ))
