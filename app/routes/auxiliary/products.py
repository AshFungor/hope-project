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


@Blueprints.product.route("/api/products/consumable")
@login_required
@function_context
def get_consumable_categories(ctx: AppContext):
    names = [name.upper() for name in ctx.config.consumption.categories]

    return jsonify({
        "consumables": names
    })


@Blueprints.product.route("/api/products/consumable")
@login_required
@function_context
def consume(ctx: AppContext):
    data = []
    for field in ["product", "account"]:
        if field not in flask.request.form:
            return flask.Response(f"missing form field: {field}")
        data.append(flask.request.form[field])

    product, account = map(int, data)
    named = env.db.impl().session.query(models.Product).get(product)

    if named.category not in norms:
        return flask.Response(f"продукт {named.name} не может быть употреблен", status=443)

    status, payload = models.Consumption.did_consume_enough(
        account, named.category, norms.get(named.category, 0), time_accounted.get(named.category, datetime.timedelta(days=1))
    )

    if isinstance(payload, str):
        logging.warning(f"internal error: {payload}")
        return flask.Response(status=500)

    # payload shows how much more we need to consume
    products = (
        env.db.impl()
        .session.execute(
            orm.select(models.Product2BankAccount).filter(
                orm.and_(models.Product2BankAccount.bank_account_id == account, models.Product2BankAccount.product_id == product)
            )
        )
        .first()[0]
    )
    has = products.count

    original = flask.request.args.get("for", None)
    if not status:
        try:
            products.count -= min(has, payload)
            env.db.impl().session.add(models.Consumption(account, product, payload, datetime.datetime.now(tz=CurrentTimezone)))

            if original is None or original.startswith("5"):
                flask_login.current_user.bonus += get_current_user_bonus(named.level)

            env.db.impl().session.commit()
        except Exception as error:
            logging.warning(f"error on consumption: {error}")
            return redirect_to_original(original, "ошибка потребления")
    else:
        return redirect_to_original(original, "норма товара уже употреблена")

    if has < payload:
        return redirect_to_original(original, f"недостаточно товаров на счету: {payload - has}")
    return redirect_to_original(original, "потребление успешно")
