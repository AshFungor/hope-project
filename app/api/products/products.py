from datetime import datetime, timedelta

import sqlalchemy as orm
from flask import Response
from flask_login import current_user, login_required

from app.api import Blueprints
from app.codegen.product import (
    ConsumableCategoriesResponse,
    ConsumeProductRequest,
    ConsumeProductResponse,
    ConsumeProductResponseStatus,
    ProductCountRequest,
    ProductCountResponse,
    ProductInfo,
    ProductListResponse,
    ProductNamesRequest,
    ProductNamesResponse,
)
from app.context import AppContext, function_context
from app.models import Consumption, Product, Product2BankAccount
from app.models.queries import needs_to_consume, wrap_crud_context
from app.api.helpers import preprocess, protobufify


@Blueprints.product.route("/api/products/all", methods=["GET"])
@login_required
@function_context
def get_all_products(ctx: AppContext):
    products = ctx.database.session.execute(orm.select(Product).order_by(orm.desc(Product.level))).scalars().all()

    return protobufify(
        ProductListResponse(
            products=[ProductInfo(id=product.id, name=product.name, category=product.category, level=product.level) for product in products]
        )
    )


@Blueprints.product.route("/api/products/names", methods=["POST"])
@login_required
@preprocess(ProductNamesRequest)
@function_context
def get_product_names(ctx: AppContext, req: ProductNamesRequest):
    results = ctx.database.session.scalars(
        orm.select(Product.name)
        .join(Product2BankAccount, Product.id == Product2BankAccount.product_id)
        .filter(Product2BankAccount.bank_account_id == req.bank_account_id, Product2BankAccount.count > 0, Product.id != 1)
    ).all()

    return protobufify(
        ProductNamesResponse(names=results)
    )


@Blueprints.product.route("/api/products/count", methods=["POST"])
@login_required
@preprocess(ProductCountRequest)
@function_context
def get_product_count(ctx: AppContext, req: ProductCountRequest):
    result = (
        ctx.database.session.execute(
            orm.select(Product2BankAccount.count)
            .join(Product, Product2BankAccount.product_id == Product.id)
            .filter(Product2BankAccount.bank_account_id == req.bank_account_id, Product.name == req.product_name)
        ).scalar_one_or_none()
        or 0
    )

    return protobufify(
        ProductCountResponse(count=result)
    )


@Blueprints.product.route("/api/products/consumable", methods=["GET"])
@login_required
@function_context
def get_consumable_categories(ctx: AppContext):
    names = [name.upper() for name in ctx.config.consumption.categories]
    return protobufify(
        ConsumableCategoriesResponse(consumables=names)
    )


@Blueprints.product.route("/api/products/consume", methods=["POST"])
@login_required
@preprocess(ConsumeProductRequest)
@function_context
def consume(ctx: AppContext, req: ConsumeProductRequest):
    product_name = req.product
    bank_account_id = req.account

    product = ctx.database.session.scalar(orm.select(Product).filter(Product.name == product_name))

    if not product:
        return protobufify(
            ConsumeProductResponse(
                ConsumeProductResponseStatus.NOT_ENOUGH
            )
        )

    consumable_categories = [category.upper() for category in ctx.config.consumption.categories]
    if product.category not in consumable_categories:
        return protobufify(
            ConsumeProductResponse(status=ConsumeProductResponseStatus.NOT_CONSUMABLE)
        )

    consumption_info = ctx.config.consumption.categories[product.category.lower()]
    left = needs_to_consume(bank_account_id, product.category, consumption_info.count, timedelta(days=consumption_info.period_days))

    products = ctx.database.session.scalar(
        orm.select(Product2BankAccount).filter(Product2BankAccount.bank_account_id == bank_account_id, Product2BankAccount.product_id == product.id)
    )

    if not products:
        return protobufify(
            ConsumeProductResponse(status=ConsumeProductResponseStatus.NOT_ENOUGH)
        )

    has = products.count
    if has < left:
        return protobufify(
            ConsumeProductResponse(status=ConsumeProductResponseStatus.NOT_ENOUGH)
        )

    with wrap_crud_context():
        products.count -= left
        ctx.database.session.add(Consumption(bank_account_id, product.id, left, datetime.now()))

        if str(bank_account_id).startswith("5"):
            bonus = product.level
            if product.level <= 3:
                bonus -= 1
            current_user.bonus += bonus

        ctx.database.session.commit()

    return protobufify(
        ConsumeProductResponse(status=ConsumeProductResponseStatus.OK)
    )
