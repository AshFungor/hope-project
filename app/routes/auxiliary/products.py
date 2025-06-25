import sqlalchemy as orm

from http import HTTPStatus
from flask import jsonify, request
from flask_login import login_required

from app.routes import Blueprints
from app.models import Product, Product2BankAccount
from app.context import function_context, AppContext


@Blueprints.product.route("/api/products/all", methods=["GET"])
@login_required
@function_context
def get_all_products(ctx: AppContext):
    products = ctx.database.session.execute(
        orm.select(Product).order_by(orm.desc(Product.level))
    ).scalars().all()

    return jsonify([
        {
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "level": product.level
        } for product in products
    ])


@Blueprints.product.route("/api/products/names", methods=["GET"])
@login_required
@function_context
def get_product_names(ctx: AppContext):
    account_id = request.args.get("bank_account_id", type=int)
    if account_id is None:
        return "Missing parameters", HTTPStatus.BAD_REQUEST

    results = ctx.database.session.scalars(
        orm.select(Product.name)
        .join(Product2BankAccount, Product.id == Product2BankAccount.product_id)
        .filter(
            Product2BankAccount.bank_account_id == account_id,
            Product2BankAccount.count > 0,
            Product.id != 1
        )
    ).all()

    return jsonify({"names": results})


@Blueprints.product.route("/api/products/count", methods=["GET"])
@login_required
@function_context
def get_product_count(ctx: AppContext):
    account_id = request.args.get("bank_account_id", type=int)
    product_name = request.args.get("product_name", type=str)

    if any(param is None for param in (account_id, product_name)):
        return "Missing parameters", HTTPStatus.BAD_REQUEST

    result = ctx.database.session.execute(
        orm.select(Product2BankAccount.count)
        .join(Product, Product2BankAccount.product_id == Product.id)
        .filter(
            Product2BankAccount.bank_account_id == account_id,
            Product.name == product_name
        )
    ).scalar_one_or_none()

    return jsonify({"count": result})
