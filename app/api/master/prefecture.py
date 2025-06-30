import sqlalchemy as orm
from flask_login import login_required

from app.api import Blueprints
from app.api.helpers import protobufify, pythonify
from app.codegen.prefecture import (
    AllPrefecturesRequest,
    AllPrefecturesResponse,
    UpdateLinkRequest,
    UpdateLinkResponse,
)
from app.codegen.types import Prefecture as PrefectureProto
from app.context import AppContext
from app.models import BankAccount, Company, Prefecture, User
from app.models.queries import wrap_crud_context


@Blueprints.master.route("/api/prefecture/all", methods=["POST"])
@login_required
@pythonify(AllPrefecturesRequest)
def get_all_prefectures(ctx: AppContext, __req: AllPrefecturesRequest):
    prefectures = ctx.database.session.scalars(orm.select(Prefecture)).all()

    entries = [
        PrefectureProto(
            name=p.name,
            bank_account_id=p.bank_account_id,
            prefect_id=p.prefect_id or 0,
            economic_assistant_id=p.economic_assistant_id,
            social_assistant_id=p.social_assistant_id or 0,
        )
        for p in prefectures
    ]

    return protobufify(AllPrefecturesResponse(prefectures=entries))


@Blueprints.master.route("/api/prefecture/link/update", methods=["POST"])
@login_required
@pythonify(UpdateLinkRequest)
def update_connection(ctx: AppContext, req: UpdateLinkRequest):
    with wrap_crud_context():
        bank_account = ctx.database.session.get(BankAccount, req.bankAccountId)
        if not bank_account:
            return protobufify(UpdateLinkResponse(success=False))

        user = ctx.database.session.get(User, req.bankAccountId)
        if user:
            user.prefecture_id = req.prefectureId
            ctx.database.session.commit()
            return protobufify(UpdateLinkResponse(success=True))

        company = ctx.database.session.get(Company, req.bankAccountId)
        if company:
            company.prefecture_id = req.prefectureId
            ctx.database.session.commit()
            return protobufify(UpdateLinkResponse(success=True))

    return protobufify(UpdateLinkResponse(success=False))
