from datetime import datetime

import sqlalchemy as orm
from flask_login import current_user, login_required

from app.api import Blueprints
from app.api.helpers import protobufify, pythonify
from app.codegen.company import (
    CreateCompanyRequest,
    CreateCompanyResponse,
    CreateCompanyResponseStatus,
)
from app.codegen.hope import Response
from app.context import AppContext
from app.models import BankAccount, Company, Prefecture, Role, User, User2Company, Product2BankAccount


@Blueprints.company.route("/api/company/create", methods=["POST"])
@login_required
@pythonify(CreateCompanyRequest)
def create_company(ctx: AppContext, req: CreateCompanyRequest):
    session = ctx.database.session

    company_exists = session.scalar(orm.select(Company).filter(Company.name == req.name))
    if company_exists:
        ctx.logger.warning(f"create company failed: duplicate name: {company_exists.name}")
        return protobufify(Response(create_company=CreateCompanyResponse(status=CreateCompanyResponseStatus.DUPLICATE_NAME)))

    prefecture = session.scalar(orm.select(Prefecture).filter(Prefecture.name == req.prefecture))

    if not prefecture:
        ctx.logger.warning(f"create company failed: prefecture not found")
        return protobufify(Response(create_company=CreateCompanyResponse(status=CreateCompanyResponseStatus.MISSING_PREFECTURE)))

    founders_ids = [f.bank_account_id for f in req.founders]
    if len(founders_ids) == 0:
        ctx.logger.warning(f"create company failed: no founders")
        return protobufify(Response(create_company=CreateCompanyResponse(status=CreateCompanyResponseStatus.MISSING_FOUNDERS)))
    
    total = sum([f.share for f in req.founders])
    if not (0.99 <= total <= 1.0):
        ctx.logger.warning(f"create company failed: shares are out of bounds: {total}")
        return protobufify(Response(create_company=CreateCompanyResponse(status=CreateCompanyResponseStatus.SHARES_ERROR)))

    if len(set(founders_ids)) != len(founders_ids):
        ctx.logger.warning(f"create company failed: {current_user.id} - duplicate founders")
        return protobufify(Response(create_company=CreateCompanyResponse(status=CreateCompanyResponseStatus.DUPLICATE_FOUNDERS)))

    users = session.scalars(orm.select(User).filter(User.bank_account_id.in_(founders_ids))).all()
    if len(users) < len(founders_ids):
        ctx.logger.warning(f"create company failed: {current_user.id} - one or more founders not found")
        return protobufify(Response(create_company=CreateCompanyResponse(status=CreateCompanyResponseStatus.MISSING_FOUNDERS)))

    ceo_user = None
    if req.ceo_bank_account_id:
        ceo_user = session.scalar(
            orm.select(User).filter(User.bank_account_id == req.ceo_bank_account_id)
        )
        if not ceo_user:
            ctx.logger.warning(f"create company failed: {current_user.id} - ceo not found")
            return protobufify(Response(create_company=CreateCompanyResponse(status=CreateCompanyResponseStatus.MISSING_FOUNDERS)))

    bank_account = BankAccount(BankAccount.from_kind(BankAccount.AccountMapping.COMPANY))
    link = Product2BankAccount(
        bank_account_id=bank_account.id,
        product_id=ctx.config.money_product_id,
        count=0
    )
    company = Company(bank_account_id=bank_account.id, prefecture_id=prefecture.id, name=req.name, about=req.about)
    session.add_all([bank_account, company, link])
    session.commit()

    for founder in req.founders:
        user = next((u for u in users if u.bank_account_id == founder.bank_account_id), None)
        if user:
            session.add(
                User2Company(
                    user_id=user.id,
                    company_id=company.id,
                    role=Role.FOUNDER,
                    ratio=round(founder.share * 100, 2),
                    employed_at=datetime.now()
                )
            )

    if ceo_user:
        session.add(
            User2Company(
                user_id=ceo_user.id,
                company_id=company.id,
                role=Role.CEO,
                ratio=0,
                employed_at=datetime.now()
            )
        )

    session.commit()

    return protobufify(Response(create_company=CreateCompanyResponse(status=CreateCompanyResponseStatus.OK)))
