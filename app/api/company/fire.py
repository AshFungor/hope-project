from datetime import datetime

import sqlalchemy as orm
from flask_login import login_required, current_user

from app.api import Blueprints
from app.api.helpers import protobufify, pythonify
from app.codegen.company import FireRequest, FireResponse, FireResponseStatus
from app.codegen.hope import Response as APIResponse
from app.context import AppContext
from app.models import Company, User, User2Company, Role


CRITICAL_ROLES = {
    Role.CEO,
    Role.CFO,
    Role.MARKETING_MANAGER,
    Role.PRODUCTION_MANAGER,
}


@Blueprints.company.route("/api/company/fire", methods=["POST"])
@login_required
@pythonify(FireRequest)
def fire_employee(ctx: AppContext, req: FireRequest):
    session = ctx.database.session

    company = session.scalar(
        orm.select(Company).filter_by(bank_account_id=req.company_bank_account_id)
    )
    if not company:
        return protobufify(APIResponse(fire=FireResponse(status=FireResponseStatus.COMPANY_NOT_FOUND)))

    employer_link = session.scalar(
        orm.select(User2Company)
        .filter(
            User2Company.fired_at == None,
            User2Company.user_id == current_user.id,
            User2Company.company_id == company.id,
            User2Company.role != Role.FOUNDER,
        )
    )
    if not employer_link:
        return protobufify(APIResponse(fire=FireResponse(status=FireResponseStatus.EMPLOYER_NOT_AUTHORIZED)))

    employer_role = employer_link.role

    employee_user = session.scalar(
        orm.select(User).filter(User.bank_account_id == req.employee_bank_account_id,)
    )
    if not employee_user:
        return protobufify(APIResponse(fire=FireResponse(status=FireResponseStatus.USER_NOT_FOUND)))

    employee_link = session.scalar(
        orm.select(User2Company)
        .filter(
            User2Company.user_id == employee_user.id,
            User2Company.company_id == company.id,
            User2Company.role != Role.FOUNDER,
            User2Company.fired_at == None,
        )
    )
    if not employee_link:
        return protobufify(APIResponse(fire=FireResponse(status=FireResponseStatus.EMPLOYEE_IS_NOT_SUITABLE)))

    employee_role = employee_link.role
    if employer_role == Role.CEO:
        pass
    elif employer_role == Role.PRODUCTION_MANAGER and employee_role == Role.EMPLOYEE:
        pass
    else:
        return protobufify(APIResponse(fire=FireResponse(status=FireResponseStatus.EMPLOYER_NOT_AUTHORIZED)))

    employee_link.fired_at = datetime.now()
    session.commit()

    return protobufify(APIResponse(fire=FireResponse(status=FireResponseStatus.OK)))
