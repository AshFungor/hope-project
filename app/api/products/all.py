import sqlalchemy as orm
from flask_login import login_required

from app.api import Blueprints
from app.api.helpers import pythonify, protobufify
from app.context import AppContext

from app.codegen.hope import Response
from app.codegen.product import (
    ProductCountsRequest,
    ProductCountsResponse,
    ProductCountsResponseProductWithCount,
    AllProductsRequest,
    AllProductsResponse,
    AvailableProductsRequest,
    AvailableProductsResponse,
)
from app.codegen.types import Product as ProductProto


from app.models import Product, Product2BankAccount


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
        orm.select(Product)
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
