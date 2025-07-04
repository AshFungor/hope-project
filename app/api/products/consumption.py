from datetime import datetime, timedelta

import sqlalchemy as orm
from flask_login import login_required

from app.api import Blueprints
from app.api.helpers import local_datetime, protobufify, pythonify
from app.codegen.hope import Response
from app.codegen.product import (
    CollectConsumersRequest,
    CollectConsumersResponse,
    ConsumptionHistoryRequest,
    ConsumptionHistoryResponse,
    ConsumptionHistoryResponseConsumptionEntry,
    ConsumptionHistoryResponseEntries,
    ConsumptionHistoryResponseError,
    ViewConsumersRequest,
    ViewConsumersResponse,
)
from app.codegen.types import Consumer, PartialUser
from app.codegen.types import Product as ProductProto
from app.context import AppContext
from app.models import BankAccount, Consumption, Product, Product2BankAccount, User
from app.models.queries import needs_to_consume, wrap_crud_context


@Blueprints.product.route("/api/products/consumers/view", methods=["POST"])
@login_required
@pythonify(ViewConsumersRequest)
def view_consumers(ctx: AppContext, req: ViewConsumersRequest):
    category = req.category.upper()
    configured = ctx.config.consumption.categories

    if category != "ALL" and category.lower() not in configured:
        return protobufify(Response(view_consumers=ViewConsumersResponse(consumers=[])))

    users = ctx.database.session.scalars(orm.select(User)).all()

    result = []
    for user in users:
        mapper = {}
        for cat in configured if category == "ALL" else [category.lower()]:
            norm = configured[cat]
            left = needs_to_consume(
                user.bank_account_id,
                cat.upper(),
                norm.count,
                timedelta(days=norm.period_days),
            )
            if left:
                mapper[cat.upper()] = f"needs {left} more"
            else:
                mapper[cat.upper()] = "ok"

        result.append(
            Consumer(
                user=PartialUser(
                    name=user.name,
                    last_name=user.last_name,
                    patronymic=user.patronymic,
                    bank_account_id=user.bank_account_id,
                ),
                category_status=mapper,
            )
        )

    return protobufify(Response(view_consumers=ViewConsumersResponse(consumers=result)))


@Blueprints.product.route("/api/products/consumers/collect", methods=["POST"])
@login_required
@pythonify(CollectConsumersRequest)
def collect_consumers(ctx: AppContext, req: CollectConsumersRequest):
    configured = ctx.config.consumption.categories
    money_product_id = ctx.config.money_product_id

    count = 0

    for user_id in req.user_ids:
        for cat in req.categories:
            cat_lower = cat.lower()
            if cat_lower not in configured:
                ctx.logger.debug(f"category {cat_lower} is not in consumables")
                continue

            norm = configured[cat_lower]

            left = needs_to_consume(
                user_id,
                cat.upper(),
                norm.count,
                timedelta(days=norm.period_days),
            )

            if not left:
                ctx.logger.debug(f"user with id {user_id} consumed enough, skipping")
                continue

            product = ctx.database.session.scalar(
                orm.select(Product).filter(
                    Product.category == cat.upper(),
                    Product.level == 1,
                )
            )

            if not product:
                ctx.logger.debug(f"product for category {cat_lower} was not found")
                continue

            money_wallet = ctx.database.session.scalar(
                orm.select(Product2BankAccount).filter(
                    Product2BankAccount.bank_account_id == user_id,
                    Product2BankAccount.product_id == money_product_id,
                )
            )

            money_wallet.count -= norm.price
            with wrap_crud_context():
                ctx.database.session.add(
                    Consumption(
                        bank_account_id=user_id,
                        product_id=product.id,
                        count=left,
                        consumed_at=datetime.now(),
                    )
                )
                count += 1

    ctx.database.session.commit()

    return protobufify(Response(collect_consumers=CollectConsumersResponse(success=True, message=f"processed: {count}")))


@Blueprints.product.route("/api/products/consumers/history", methods=["POST"])
@login_required
@pythonify(ConsumptionHistoryRequest)
def history(ctx: AppContext, req: ConsumptionHistoryRequest):
    account = ctx.database.session.get(BankAccount, req.bank_account_id)

    if account is None:
        return protobufify(
            Response(view_consumption_history=ConsumptionHistoryResponse(error=ConsumptionHistoryResponseError.BANK_ACCOUNT_NOT_FOUND))
        )

    if not str(account.id).startswith(str(ctx.config.account_mapping.user)):
        return protobufify(Response(view_consumption_history=ConsumptionHistoryResponse(error=ConsumptionHistoryResponseError.NOT_A_USER)))

    results = ctx.database.session.execute(
        orm.select(Consumption, Product).filter(Consumption.bank_account_id == account.id).join(Product, Product.id == Consumption.product_id)
    ).all()

    response = []
    for consumption, product in results:
        response.append(
            ConsumptionHistoryResponseConsumptionEntry(
                consumed_at=local_datetime(ctx, consumption.consumed_at).strftime("%Y-%m-%d %H:%M"),
                count=consumption.count,
                product=ProductProto(
                    name=product.name,
                    category=product.category,
                    level=product.level,
                ),
            )
        )

    return protobufify(Response(view_consumption_history=ConsumptionHistoryResponse(entries=ConsumptionHistoryResponseEntries(entries=response))))
