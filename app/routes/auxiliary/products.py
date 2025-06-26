import sqlalchemy as orm

from http import HTTPStatus
from datetime import timedelta, datetime
from flask import jsonify, request
from flask_login import login_required, current_user

from app.routes import Blueprints
from app.routes.queries import wrap_crud_call
from app.context import function_context, AppContext
from app.routes.queries.common import did_consume_enough
from app.models import Product, Product2BankAccount, Consumption


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


@Blueprints.product.route("/api/products/consumable")
@login_required
@function_context
def get_consumable_categories(ctx: AppContext):
    names = [name.upper() for name in ctx.config.consumption.categories]

    return jsonify({
        "consumables": names
    })


@Blueprints.product.route("/api/products/consume", methods=["POST"])
@login_required
@function_context
def consume(ctx: AppContext):
    product_name = request.json.get("product")
    bank_account_id = request.json.get("account")
    if any(param is None for param in (product_name, bank_account_id)):
        return "Missing parameters", HTTPStatus.BAD_REQUEST
    
    try:
        bank_account_id = int(bank_account_id)
    except ValueError:
        return "Type mismatch for parameters", HTTPStatus.BAD_REQUEST

    product = ctx.database.session.scalar(
        orm
        .select(Product)
        .filter(Product.name == product_name)
    )

    consumable_categories = [category.upper() for category in ctx.config.consumption.categories]
    if product.category not in consumable_categories:
        return f"product {product.name} cannot be consumed", HTTPStatus.BAD_REQUEST

    consumption_info = ctx.config.consumption.categories[product.category.lower()]
    status, payload = did_consume_enough(
        bank_account_id,
        product.category,
        consumption_info.count,
        timedelta(days=consumption_info.period_days)
    )

    if isinstance(payload, str):
        return f"error: {payload}", HTTPStatus.NOT_ACCEPTABLE

    # payload shows how much more we need to consume
    products = ctx.database.session.scalar(
        orm
        .select(Product2BankAccount)
        .filter(orm
            .and_(
                Product2BankAccount.bank_account_id == bank_account_id,
                Product2BankAccount.product_id == product.id
            )
        )
    )

    has = products.count
    if status:
        return "already consumed enough", HTTPStatus.CONFLICT

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

    if has < payload:
        return f"missing products: {abs(payload - has)}", HTTPStatus.NOT_ACCEPTABLE
    
    __create()
    return "successful", HTTPStatus.OK
