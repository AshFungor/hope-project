import sqlalchemy as orm
from flask_login import login_required

from app.api import Blueprints
from app.api.helpers import protobufify, pythonify
from app.codegen.company import GetCompanyRequest, GetCompanyResponse
from app.codegen.types import Company as CompanyProto
from app.codegen.hope import Response

from app.context import AppContext
from app.models import Company


@Blueprints.company.route("/api/company/get", methods=["POST"])
@login_required
@pythonify(GetCompanyRequest)
def get_company(ctx: AppContext, req: GetCompanyRequest):
    session = ctx.database.session

    company = session.scalar(
        orm.select(Company).filter_by(bank_account_id=req.company_bank_account_id)
    )

    if not company:
        return protobufify(GetCompanyResponse())

    prefecture_bank_account = company.prefecture.bank_account_id if company.prefecture else 0
    return protobufify(
        Response(get_company=GetCompanyResponse(
                company=CompanyProto(
                    bank_account_id=company.bank_account_id,
                    name=company.name,
                    about=company.about,
                    prefecture_bank_account_id=prefecture_bank_account
                )
            )
        )
    )
