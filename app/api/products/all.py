import sqlalchemy as orm
from flask_login import login_required

from app.api import Blueprints
from app.api.helpers import protobufify, pythonify
from app.codegen.hope import Response as APIResponse
from app.codegen.product import (
    AllProductsRequest,
    AllProductsResponse,
    AvailableProductsRequest,
    AvailableProductsResponse,
    ProductCountsRequest,
    ProductCountsResponse,
    ProductCountsResponseProductWithCount,
)
from app.codegen.types import Product as ProductProto
from app.context import AppContext
from app.models import Product, Product2BankAccount


@Blueprints.product.route("/api/products/all", methods=["POST"])
@login_required
@pythonify(AllProductsRequest)
def all_products(ctx: AppContext, __req: AllProductsRequest):
    products = ctx.database.session.scalars(
        orm.select(Product).order_by(orm.desc(Product.level))
    ).all()

    consumables = [name.upper() for name in ctx.config.consumption.categories]

    return protobufify(
        APIResponse(
            all_products=AllProductsResponse(
                products=[
                    ProductProto(
                        name=product.name,
                        category=product.category,
                        level=product.level,
                        consumable=product.category.upper() in consumables,
                    )
                    for product in products
                ]
            )
        )
    )


@Blueprints.product.route("/api/products/available", methods=["POST"])
@login_required
@pythonify(AvailableProductsRequest)
def available_products(ctx: AppContext, req: AvailableProductsRequest):
    products = ctx.database.session.scalars(
        orm.select(Product)
        .join(Product2BankAccount, Product.id == Product2BankAccount.product_id)
        .filter(
            Product2BankAccount.bank_account_id == req.bank_account_id,
            Product2BankAccount.count > 0,
            Product.id != 1,  # assuming product ID 1 is "money"
        )
    ).all()

    consumables = [name.upper() for name in ctx.config.consumption.categories]

    return protobufify(
        APIResponse(
            available_products=AvailableProductsResponse(
                products=[
                    ProductProto(
                        name=product.name,
                        category=product.category,
                        level=product.level,
                        consumable=product.category.upper() in consumables,
                    )
                    for product in products
                ]
            )
        )
    )


@Blueprints.product.route("/api/products/counts", methods=["POST"])
@login_required
@pythonify(ProductCountsRequest)
def get_product_count(ctx: AppContext, req: ProductCountsRequest):
    products = ctx.database.session.execute(
        orm.select(Product, Product2BankAccount.count)
        .join(Product, Product2BankAccount.product_id == Product.id)
        .filter(Product2BankAccount.bank_account_id == req.bank_account_id)
    ).all()

    consumables = [name.upper() for name in ctx.config.consumption.categories]

    return protobufify(
        APIResponse(
            product_counts=ProductCountsResponse(
                products=[
                    ProductCountsResponseProductWithCount(
                        product=ProductProto(
                            name=product.name,
                            category=product.category,
                            level=product.level,
                            consumable=product.category.upper() in consumables,
                        ),
                        count=count,
                    )
                    for product, count in products
                ]
            )
        )
    )
