import sqlalchemy as orm

from datetime import datetime

from flask_login import login_required, current_user

from app.api import Blueprints
from app.api.helpers import protobufify, pythonify

from app.context import AppContext
from app.models import Company, User, User2Company, Role
from app.models.queries import wrap_crud_context

from app.codegen.hope import Response
from app.codegen.types import EmployeeRole
from app.codegen.company import EmployRequest, EmployResponse, EmployResponseStatus, MasterChangeCEOResponse, MasterChangeCEORequest


CRITICAL_ROLES = {
    EmployeeRole.CEO,
    EmployeeRole.CFO,
    EmployeeRole.MARKETING_MANAGER,
    EmployeeRole.PRODUCTION_MANAGER,
}

# Mapping from EmployeeRole to Role for database queries
EMPLOYEE_ROLE_TO_DB_ROLE = {
    EmployeeRole.CEO: Role.CEO,
    EmployeeRole.CFO: Role.CFO,
    EmployeeRole.MARKETING_MANAGER: Role.MARKETING_MANAGER,
    EmployeeRole.PRODUCTION_MANAGER: Role.PRODUCTION_MANAGER,
    EmployeeRole.EMPLOYEE: Role.EMPLOYEE,
    EmployeeRole.FOUNDER: Role.FOUNDER,
}


@Blueprints.company.route("/api/company/employ", methods=["POST"])
@login_required
@pythonify(EmployRequest)
def employ_user(ctx: AppContext, req: EmployRequest):
    def answer(msg: EmployResponse):
        return protobufify(Response(employ=msg))

    session = ctx.database.session
    employer = current_user

    user = session.scalar(
        orm.select(User).filter(User.bank_account_id == req.new_employee_bank_account_id)
    )
    if not user:
        ctx.logger.warning(f"employment failed: could not find employee: {req.new_employee_bank_account_id}")
        return answer(EmployResponse(status=EmployResponseStatus.USER_NOT_FOUND))

    company = session.scalar(
        orm.select(Company).filter_by(bank_account_id=req.company_bank_account_id)
    )
    if not company:
        ctx.logger.warning(f"employment failed: could not find company: {req.company_bank_account_id}")
        return answer(EmployResponse(status=EmployResponseStatus.COMPANY_NOT_FOUND))

    employer_link = session.scalar(
        orm
        .select(User2Company)
        .filter(
            orm.and_(
                User2Company.fired_at == None,
                User2Company.user_id == employer.id,
                User2Company.company_id == company.id,
                # founders are not considered when employing
                User2Company.role != Role.FOUNDER,
            )
        )
    )
    if not employer_link:
        ctx.logger.warning(
            f"employment failed: employer {employer.id} is not related to company: {req.company_bank_account_id}"
        )
        return answer(EmployResponse(status=EmployResponseStatus.USER_NOT_FOUND))

    employer_role = employer_link.role
    if employer_role == Role.CEO:
        # should we remove ceo from payload?
        if req.role == EmployeeRole.CEO:
            ctx.logger.warning(
                f"employment failed: cannot employ ceo"
            )
            return answer(EmployResponse(status=EmployResponseStatus.EMPLOYER_NOT_AUTHORIZED))
        pass
    elif employer_role == Role.PRODUCTION_MANAGER:
        if req.role != EmployeeRole.EMPLOYEE:
            ctx.logger.warning(
                f"employment failed: employment for employees works for production manager only"
            )
            return answer(EmployResponse(status=EmployResponseStatus.EMPLOYEE_IS_NOT_SUITABLE))
    else:
        ctx.logger.warning(
            f"employment failed: employer must be CEO or production manager, current: {employer_role}"
        )
        return answer(EmployResponse(status=EmployResponseStatus.EMPLOYER_NOT_AUTHORIZED))

    if req.role in CRITICAL_ROLES:
        other_critical = session.scalar(
            orm.select(User2Company)
            .filter(
                User2Company.fired_at == None,
                User2Company.user_id == user.id,
                User2Company.company_id == company.id,
                User2Company.role.in_([EMPLOYEE_ROLE_TO_DB_ROLE[r] for r in [*CRITICAL_ROLES, EmployeeRole.EMPLOYEE]])
            )
        )
        if other_critical:
            ctx.logger.warning(
                f"employment failed: employee already takes critical role"
            )
            return answer(EmployResponse(status=EmployResponseStatus.HAS_ROLE_ALREADY))
        
    current_employee = session.scalar(
        orm.select(User2Company)
        .filter(
            User2Company.fired_at == None,
            User2Company.company_id == company.id,
            User2Company.role == EMPLOYEE_ROLE_TO_DB_ROLE[req.role],
        )
    )

    if current_employee:
        ctx.logger.warning(f"employment failed: user {current_employee.id} already takes position")
        return answer(EmployResponse(status=EmployResponseStatus.ALREADY_TAKEN))

    with wrap_crud_context():
        link = User2Company(
            user_id=user.id,
            company_id=company.id,
            role=EMPLOYEE_ROLE_TO_DB_ROLE[req.role],
            ratio=0,
            employed_at=datetime.now()
        )
        session.add(link)
        session.commit()

    return answer(EmployResponse(status=EmployResponseStatus.OK))


@Blueprints.company.route("/api/company/master/change_ceo", methods=["POST"])
@login_required
@pythonify(MasterChangeCEORequest)
def master_change_ceo(ctx: AppContext, req: MasterChangeCEORequest):
    session = ctx.database.session

    company = session.scalar(
        orm.select(Company).filter_by(bank_account_id=req.company_id)
    )
    new_ceo = session.scalar(
        orm.select(User).filter_by(bank_account_id=req.new_ceo_id)
    )

    if not company or not new_ceo:
        return protobufify(Response(master_change_ceo=MasterChangeCEOResponse(ok=False)))

    current_ceo_link = session.scalar(
        orm.select(User2Company).filter(
            User2Company.company_id == company.id,
            User2Company.role == Role.CEO,
            User2Company.fired_at.is_(None)
        )
    )

    if current_ceo_link:
        current_ceo_link.fired_at = datetime.now()

    new_ceo_link = session.scalar(
        orm.select(User2Company).filter(
            User2Company.company_id == company.id,
            User2Company.user_id == new_ceo.id,
            User2Company.fired_at.is_(None)
        )
    )

    if new_ceo_link:
        new_ceo_link.role = Role.CEO
    else:
        new_ceo_link = User2Company(
            user_id=new_ceo.id,
            company_id=company.id,
            role=Role.CEO,
            employed_at=datetime.now(),
            ratio=0
        )
        session.add(new_ceo_link)

    company.ceo_id = new_ceo.id

    with wrap_crud_context():
        session.commit()

    return protobufify(Response(master_change_ceo=MasterChangeCEOResponse(ok=True)))