import sqlalchemy as orm
from flask_login import login_required

from app.api import Blueprints
from app.api.helpers import protobufify, pythonify
from app.codegen.company import AllEmployeesRequest, AllEmployeesResponse, AllEmployeesResponseEmployee
from app.codegen.types import PartialUser, EmployeeRole
from app.codegen.hope import Response

from app.context import AppContext
from app.models import Company, User, User2Company, Role


DB_ROLE_TO_PROTO = {
    Role.CEO: EmployeeRole.CEO,
    Role.CFO: EmployeeRole.CFO,
    Role.MARKETING_MANAGER: EmployeeRole.MARKETING_MANAGER,
    Role.PRODUCTION_MANAGER: EmployeeRole.PRODUCTION_MANAGER,
    Role.EMPLOYEE: EmployeeRole.EMPLOYEE,
    Role.FOUNDER: EmployeeRole.FOUNDER,
}


@Blueprints.company.route("/api/company/employees", methods=["POST"])
@login_required
@pythonify(AllEmployeesRequest)
def get_all_employees(ctx: AppContext, req: AllEmployeesRequest):
    session = ctx.database.session

    company = session.scalar(
        orm.select(Company).filter_by(bank_account_id=req.company_bank_account_id)
    )

    if not company:
        return protobufify(AllEmployeesResponse(employees=[]))

    results = session.execute(
        orm.select(User, User2Company)
        .join(User2Company, User.id == User2Company.user_id)
        .filter(
            orm.and_(
                User2Company.fired_at == None,
                User2Company.company_id == company.id),
                User2Company.role != Role.FOUNDER
            )
    ).all()

    employees = [
        AllEmployeesResponseEmployee(
            info=PartialUser(
                name=user.name,
                last_name=user.last_name,
                patronymic=user.patronymic,
                bank_account_id=user.bank_account_id,
            ),
            role=DB_ROLE_TO_PROTO[link.role]
        )
        for user, link in results
    ]

    return protobufify(Response(all_employees=AllEmployeesResponse(employees=employees)))
