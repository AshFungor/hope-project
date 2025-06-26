import sqlalchemy as orm

from http import HTTPStatus
from datetime import timedelta, datetime
from flask import request, Response
from flask_login import login_required, current_user

from app.api import Blueprints
from app.models.queries import wrap_crud_call
from app.context import function_context, AppContext
from app.models.queries import did_consume_enough
from app.models import Product, Product2BankAccount, Consumption
from app.codegen.product import (
    ProductInfo,
    ProductListResponse,
    ConsumableCategoriesResponse,
    ProductCountRequest,
    ProductCountResponse,
    ProductNamesRequest,
    ProductNamesResponse,
    ConsumeProductRequest,
    ConsumeProductResponse,
    ConsumeProductResponseStatus,
)


@Blueprints.product.route("/api/products/all", methods=["GET"])
@login_required
@function_context
def get_all_products(ctx: AppContext):
    products = ctx.database.session.execute(
        orm.select(Product).order_by(orm.desc(Product.level))
    ).scalars().all()

    res = ProductListResponse(
        products=[
            ProductInfo(
                id=product.id,
                name=product.name,
                category=product.category,
                level=product.level
            ) for product in products
        ]
    )
    return Response(bytes(res), content_type='application/protobuf')


@Blueprints.product.route("/api/products/names", methods=["POST"])
@login_required
@function_context
def get_product_names(ctx: AppContext):
    try:
        req = ProductNamesRequest().parse(request.data)
    except Exception:
        return Response(status=HTTPStatus.BAD_REQUEST)

    results = ctx.database.session.scalars(
        orm.select(Product.name)
        .join(Product2BankAccount, Product.id == Product2BankAccount.product_id)
        .filter(
            Product2BankAccount.bank_account_id == req.bank_account_id,
            Product2BankAccount.count > 0,
            Product.id != 1
        )
    ).all()

    res = ProductNamesResponse(names=results)
    return Response(bytes(res), content_type='application/protobuf')


@Blueprints.product.route("/api/products/count", methods=["POST"])
@login_required
@function_context
def get_product_count(ctx: AppContext):
    try:
        req = ProductCountRequest().parse(request.data)
    except Exception:
        return Response(status=HTTPStatus.BAD_REQUEST)

    result = ctx.database.session.execute(
        orm.select(Product2BankAccount.count)
        .join(Product, Product2BankAccount.product_id == Product.id)
        .filter(
            Product2BankAccount.bank_account_id == req.bank_account_id,
            Product.name == req.product_name
        )
    ).scalar_one_or_none() or 0

    res = ProductCountResponse(count=result)
    return Response(bytes(res), content_type='application/protobuf')


@Blueprints.product.route("/api/products/consumable", methods=["GET"])
@login_required
@function_context
def get_consumable_categories(ctx: AppContext):
    names = [name.upper() for name in ctx.config.consumption.categories]
    res = ConsumableCategoriesResponse(consumables=names)
    return Response(bytes(res), content_type='application/protobuf')


@Blueprints.product.route("/api/products/consume", methods=["POST"])
@login_required
@function_context
def consume(ctx: AppContext):
    try:
        req = ConsumeProductRequest().parse(request.data)
    except Exception:
        res = ConsumeProductResponse(
            status=ConsumeProductResponseStatus.MISSING_PARAMETERS,
            message="Invalid protobuf payload"
        )
        return Response(bytes(res), content_type='application/protobuf', status=HTTPStatus.BAD_REQUEST)

    product_name = req.product
    bank_account_id = req.account

    product = ctx.database.session.scalar(
        orm.select(Product).filter(Product.name == product_name)
    )

    if not product:
        res = ConsumeProductResponse(
            status=ConsumeProductResponseStatus.ERROR,
            message="Product not found"
        )
        return Response(bytes(res), content_type='application/protobuf', status=HTTPStatus.NOT_FOUND)

    consumable_categories = [category.upper() for category in ctx.config.consumption.categories]
    if product.category not in consumable_categories:
        res = ConsumeProductResponse(
            status=ConsumeProductResponseStatus.NOT_CONSUMABLE,
            message=f"Product {product.name} cannot be consumed"
        )
        return Response(bytes(res), content_type='application/protobuf', status=HTTPStatus.BAD_REQUEST)

    consumption_info = ctx.config.consumption.categories[product.category.lower()]
    status, payload = did_consume_enough(
        bank_account_id,
        product.category,
        consumption_info.count,
        timedelta(days=consumption_info.period_days)
    )

    if isinstance(payload, str):
        res = ConsumeProductResponse(
            status=ConsumeProductResponseStatus.ERROR,
            message=payload
        )
        return Response(bytes(res), content_type='application/protobuf', status=HTTPStatus.NOT_ACCEPTABLE)

    products = ctx.database.session.scalar(
        orm.select(Product2BankAccount)
        .filter(
            Product2BankAccount.bank_account_id == bank_account_id,
            Product2BankAccount.product_id == product.id
        )
    )

    if not products:
        res = ConsumeProductResponse(
            status=ConsumeProductResponseStatus.NOT_ACCEPTABLE,
            message="No product count available"
        )
        return Response(bytes(res), content_type='application/protobuf', status=HTTPStatus.NOT_ACCEPTABLE)

    has = products.count
    if status:
        res = ConsumeProductResponse(
            status=ConsumeProductResponseStatus.ALREADY_CONSUMED,
            message="Already consumed enough"
        )
        return Response(bytes(res), content_type='application/protobuf', status=HTTPStatus.CONFLICT)

    if has < payload:
        res = ConsumeProductResponse(
            status=ConsumeProductResponseStatus.NOT_ACCEPTABLE,
            message=f"Missing products: {abs(payload - has)}"
        )
        return Response(bytes(res), content_type='application/protobuf', status=HTTPStatus.NOT_ACCEPTABLE)

    @wrap_crud_call
    def __create():
        products.count -= min(has, payload)
        ctx.database.session.add(Consumption(bank_account_id, product.id, payload, datetime.now()))

        if str(bank_account_id).startswith("5"):
            bonus = product.level
            if product.level <= 3:
                bonus -= 1
            current_user.bonus += bonus

        ctx.database.session.commit()

    __create()

    res = ConsumeProductResponse(
        status=ConsumeProductResponseStatus.SUCCESS,
        message="successful"
    )
    return Response(bytes(res), content_type='application/protobuf')
