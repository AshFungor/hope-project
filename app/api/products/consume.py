from datetime import datetime, timedelta

import sqlalchemy as orm
from flask_login import current_user, login_required

from app.api import Blueprints
from app.api.helpers import pythonify, protobufify
from app.context import AppContext

from app.codegen.hope import Response
from app.codegen.product import (
    ConsumeProductRequest,
    ConsumeProductResponse,
    ConsumeProductResponseStatus,
)


from app.models import Consumption, Product, Product2BankAccount
from app.models.queries import needs_to_consume, wrap_crud_context


@Blueprints.product.route("/api/products/consume", methods=["POST"])
@login_required
@pythonify(ConsumeProductRequest)
def consume(ctx: AppContext, req: ConsumeProductRequest):
    product_name = req.product
    bank_account_id = req.account

    product = ctx.database.session.scalar(
        orm.select(Product).filter(Product.name == product_name)
    )

    if not product:
        return protobufify(
            Response(consume_product=ConsumeProductResponse(status=ConsumeProductResponseStatus.NOT_ENOUGH))
        )

    consumable_categories = [category.upper() for category in ctx.config.consumption.categories]
    if product.category not in consumable_categories:
        return protobufify(
            Response(consume_product=ConsumeProductResponse(status=ConsumeProductResponseStatus.NOT_CONSUMABLE))
        )

    consumption_info = ctx.config.consumption.categories[product.category.lower()]
    left = needs_to_consume(
        bank_account_id,
        product.category,
        consumption_info.count,
        timedelta(days=consumption_info.period_days)
    )

    products = ctx.database.session.scalar(
        orm.select(Product2BankAccount)
        .filter(
            Product2BankAccount.bank_account_id == bank_account_id,
            Product2BankAccount.product_id == product.id
        )
    )

    if not products:
        return protobufify(
            Response(consume_product=ConsumeProductResponse(status=ConsumeProductResponseStatus.NOT_ENOUGH))
        )

    if not left:
        return protobufify(
            Response(consume_product=ConsumeProductResponse(status=ConsumeProductResponseStatus.ALREADY_CONSUMED))
        )

    has = products.count
    if has < left:
        return protobufify(
            Response(consume_product=ConsumeProductResponse(status=ConsumeProductResponseStatus.NOT_ENOUGH))
        )

    with wrap_crud_context():
        products.count -= left
        ctx.database.session.add(
            Consumption(bank_account_id, product.id, left, datetime.now())
        )

        if str(bank_account_id).startswith("5"):
            bonus = product.level
            if product.level <= 3:
                bonus -= 1
            current_user.bonus += bonus

        ctx.database.session.commit()

    return protobufify(Response(consume_product=ConsumeProductResponse(status=ConsumeProductResponseStatus.OK)))
