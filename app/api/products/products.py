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
    ProductCountsRequest,
    ProductCountsResponse,
    ProductCountsResponseProductWithCount,
    AllProductsRequest,
    AllProductsResponse,
    AvailableProductsRequest,
    AvailableProductsResponse,
)
from app.codegen.types import Product as ProductProto


from app.models import Consumption, Product, Product2BankAccount
from app.models.queries import needs_to_consume, wrap_crud_context


@Blueprints.product.route("/api/products/all", methods=["POST"])
@login_required
@pythonify(AllProductsRequest)
def all_products(ctx: AppContext, __req: AllProductsRequest):
    products = ctx.database.session.execute(
        orm.select(Product).order_by(orm.desc(Product.level))
    ).scalars().all()

    consumables = [name.upper() for name in ctx.config.consumption.categories]
    return protobufify(Response(
        all_products=AllProductsResponse(
            products=[
                ProductProto(
                    id=product.id,
                    name=product.name,
                    category=product.category,
                    level=product.level,
                    consumable=product.category in consumables
                ) for product in products
            ]
        )
    ))


@Blueprints.product.route("/api/products/available", methods=["POST"])
@login_required
@pythonify(AvailableProductsRequest)
def available_products(ctx: AppContext, req: AvailableProductsRequest):
    products = ctx.database.session.scalars(
        orm.select(Product.name)
        .join(Product2BankAccount, Product.id == Product2BankAccount.product_id)
        .filter(
            Product2BankAccount.bank_account_id == req.bank_account_id,
            Product2BankAccount.count > 0,
            Product.id != 1
        )
    ).all()

    consumables = [name.upper() for name in ctx.config.consumption.categories]
    return protobufify(Response(
        available_products=AvailableProductsResponse(
            products=[
                ProductProto(
                    id=product.id,
                    name=product.name,
                    category=product.category,
                    level=product.level,
                    consumable=product.category in consumables
                ) for product in products
            ]
        )
    ))


@Blueprints.product.route("/api/products/counts", methods=["POST"])
@login_required
@pythonify(ProductCountsRequest)
def get_product_count(ctx: AppContext, req: ProductCountsRequest):
    products = ctx.database.session.execute(
        orm.select(Product, Product2BankAccount.count)
        .join(Product, Product2BankAccount.product_id == Product.id)
        .filter(
            Product2BankAccount.bank_account_id == req.bank_account_id
        )
    ).all()

    consumables = [name.upper() for name in ctx.config.consumption.categories]
    return protobufify(Response(
        product_counts=ProductCountsResponse(
            [
                ProductCountsResponseProductWithCount(
                    product=ProductProto(
                        id=product.id,
                        name=product.name,
                        category=product.category,
                        level=product.level,
                        consumable=product.category in consumables
                    ),
                    count=count
                ) for product, count in products
            ]
        )
    ))


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
