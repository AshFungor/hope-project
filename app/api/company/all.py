import sqlalchemy as orm
from flask_login import login_required

from app.api import Blueprints
from app.api.helpers import protobufify, pythonify
from app.codegen.company import AllCompaniesRequest, AllCompaniesResponse
from app.codegen.types import Company as CompanyProto
from app.codegen.hope import Response

from app.context import AppContext
from app.models import Company, User, User2Company


@Blueprints.company.route("/api/company/all", methods=["POST"])
@login_required
@pythonify(AllCompaniesRequest)
def get_all_companies(ctx: AppContext, req: AllCompaniesRequest):
    session = ctx.database.session

    companies = []

    if req.related_user_bank_account_id:
        user = session.scalar(
            orm.select(User).filter(User.bank_account_id == req.related_user_bank_account_id)
        )
        if not user:
            return protobufify(AllCompaniesResponse(companies=[]))

        companies = session.scalars(
            orm.select(Company)
            .join(User2Company, Company.id == User2Company.company_id)
            .filter(User2Company.user_id == user.id)
        ).all()

    elif req.globally:
        companies = session.scalars(
            orm.select(Company)
        ).all()

    else:
        return protobufify(AllCompaniesResponse(companies=[]))

    proto_companies = []
    for company in companies:
        prefecture_bank_account = company.prefecture.bank_account_id if company.prefecture else 0
        proto_companies.append(
            CompanyProto(
                bank_account_id=company.bank_account_id,
                name=company.name,
                about=company.about,
                prefecture_bank_account_id=prefecture_bank_account
            )
        )

    return protobufify(
        Response(all_companies=AllCompaniesResponse(
                companies=proto_companies
            )
        )
    )
