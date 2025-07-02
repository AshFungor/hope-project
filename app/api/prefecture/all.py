import sqlalchemy as orm

from typing import Optional
from flask_login import login_required

from app.api import Blueprints
from app.context import AppContext
from app.api.helpers import protobufify, pythonify

from app.models.queries import wrap_crud_context
from app.models import BankAccount, Company, Prefecture, User

from app.codegen.hope import Response
from app.codegen.prefecture import (
    AllPrefecturesRequest,
    AllPrefecturesResponse,
    UpdateLinkRequest,
    UpdateLinkResponse,
    CurrentPrefectureRequest,
    CurrentPrefectureResponse
)
from app.codegen.types import Prefecture as PrefectureProto


@Blueprints.master.route("/api/prefecture/all", methods=["POST"])
@login_required
@pythonify(AllPrefecturesRequest)
def get_all_prefectures(ctx: AppContext, __req: AllPrefecturesRequest):
    prefectures = ctx.database.session.scalars(orm.select(Prefecture)).all()

    entries = []
    for p in prefectures:
        prefect_bank_acount = p.prefect.bank_account_id if p.prefect else 0
        economic_assistant_bank_acount = p.prefect.bank_account_id if p.prefect else 0
        social_assistant_account = p.prefect.bank_account_id if p.prefect else 0
        entries.append(
            PrefectureProto(
                name=p.name,
                bank_account_id=p.bank_account_id,
                prefect_account_id=prefect_bank_acount,
                economic_assistant_account_id=economic_assistant_bank_acount,
                social_assistant_account_id=social_assistant_account,
            )
        )

    return protobufify(Response(all_prefectures=AllPrefecturesResponse(prefectures=entries)))


@Blueprints.master.route("/api/prefecture/link/update", methods=["POST"])
@login_required
@pythonify(UpdateLinkRequest)
def update_connection(ctx: AppContext, req: UpdateLinkRequest):
    with wrap_crud_context():
        bank_account = ctx.database.session.get(BankAccount, req.bank_account_id)
        if not bank_account:
            return protobufify(
                Response(update_prefecture_link=UpdateLinkResponse(success=False))
            )

        user = ctx.database.session.get(User, req.bank_account_id)
        if user:
            user.prefecture_id = req.prefectureId
            ctx.database.session.commit()
            return protobufify(
                Response(update_prefecture_link=UpdateLinkResponse(success=True))
            )

        company = ctx.database.session.get(Company, req.bank_account_id)
        if company:
            company.prefecture_id = req.prefectureId
            ctx.database.session.commit()
            return protobufify(
                Response(update_prefecture_link=UpdateLinkResponse(success=True))
            )

    return protobufify(Response(update_prefecture_link=UpdateLinkResponse(success=False)))


@Blueprints.master.route("/api/prefecture/current", methods=["POST"])
@login_required
@pythonify(CurrentPrefectureRequest)
def get_current_prefecture(ctx: AppContext, req: CurrentPrefectureRequest):
    session = ctx.database.session
    prefecture: Optional[Prefecture] = None

    user = session.scalar(
        orm.select(User).filter(User.bank_account_id == req.bank_account_id)
    )
    if user and user.prefecture_id:
        prefecture = session.get(Prefecture, user.prefecture_id)

    if not prefecture:
        company = session.scalar(
            orm.select(Company).filter(Company.bank_account_id == req.bank_account_id)
        )
        if company and company.prefecture_id:
            prefecture = session.get(Prefecture, company.prefecture_id)

    if not prefecture:
        return protobufify(Response(current_prefecture=None))

    entry = PrefectureProto(
        name=prefecture.name,
        bank_account_id=prefecture.bank_account_id,
        prefect_account_id=prefecture.prefect.bank_account_id if prefecture.prefect else 0,
        economic_assistant_account_id=prefecture.economic_assistant.bank_account_id if prefecture.economic_assistant else 0,
        social_assistant_account_id=prefecture.social_assistant.bank_account_id if prefecture.social_assistant else 0,
    )

    return protobufify(Response(current_prefecture=CurrentPrefectureResponse(prefecture=entry)))
