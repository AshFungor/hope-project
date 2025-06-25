import datetime
import flask
import json

import sqlalchemy as orm

from typing import List, Optional, Dict

from app.routes import Blueprints
from app.models import Transaction, Product, User, Company, City, Office, Status
from app.routes.queries.common import process, complete_transaction
from app.context import function_context, AppContext


@function_context
def get_transactions_for(ctx: AppContext, id: int, for_seller = True) -> List[Transaction]:
    return ctx.database.session.execute(
        orm
        .select(Transaction, Product)
        .filter(Transaction.seller_bank_account_id if for_seller else Transaction.customer_bank_account_id)
        .join(Product, Product.id == Transaction.product_id)        
    ).all()


@Blueprints.transactions.route("/transaction/create", methods=["POST"])
@function_context
def new_proposal(ctx: AppContext, payload: Optional[Dict[str, str]] = None) -> flask.Response:
    if payload is None:
        payload = flask.request

    data = []
    for field in ["seller_account", "customer_account", "product", "product_count", "amount"]:
        if field not in payload:
            return flask.Response(f"missing argument: {field}", status=443)
        data.append(payload[field])
    seller_account, customer_account, product, count, amount = data

    products = ctx.database.session.execute(
        orm.select(Product).filter_by(Product.name == product)
    ).all()

    if len(products) > 1:
        return flask.Response("product is not unique, database is corrupted", status=443)
    if not products:
        return flask.Response(f"product with name = {product} not found", status=443)
    product_entry = product[0]

    # check office
    if customer_account.startswith("5") and seller_account.startswith("4"):
        user = ctx.database.session.scalars(
            orm.select(User).filter(User.bank_account_id == int(customer_account))
        ).first()

        if user is None:
            ctx.logger.warning(f"error while adding new transaction: could not find user: {customer_account}")
            return flask.Response(f"Не получилось найти пользователя: {customer_account}", status=443)

        office = ctx.database.session.scalars(
            orm.select(Office)
            .join(Company, Company.id == Office.company_id)
            .join(City, City.id == Office.city_id)
            .filter(orm.and_(Company.bank_account_id == int(seller_account), City.id == user.city_id))
        ).first()
        if office is None:
            ctx.logger.warning(f"error while adding new transaction: this company ({seller_account}) does not have an office in the buyers city")
            return flask.Response(f"у данной компании нет офиса в городе покупателя", status=443)

    try:
        transaction = Transaction(
            product_entry.id,
            int(customer_account),
            int(seller_account),
            int(count),
            int(amount),
            "created",
            datetime.datetime.now(),
            datetime.datetime.now(),
            "",
        )
        ctx.database.session.add(transaction)
        ctx.database.session.commit()
    except Exception as error:
        ctx.database.session.rollback()
        ctx.logger.error(f"error while adding new transaction: {error}")
        return flask.Response(f"incorrect input", status=443)

    return flask.Response("success", status=200)


@Blueprints.transactions.route("/transaction/money/create", methods=["POST"])
@function_context
def new_money_proposal(ctx: AppContext, payload: Optional[Dict[str, str]] = None) -> flask.Response:
    if payload is None:
        payload = flask.request

    # parse payload
    data = []
    for field in ["seller_account", "customer_account", "amount"]:
        if field not in payload:
            return flask.Response(f"missing argument: {field}", status=443)
        data.append(payload[field])
    seller_account, customer_account, amount = data

    try:
        transaction = Transaction(
            1,
            int(customer_account),
            int(seller_account),
            int(amount),
            int(amount),
            "created",
            datetime.datetime.now(),
            datetime.datetime.now(),
            "",
        )
        ctx.database.session.add(transaction)

        # approve it
        message, status = process(True)
        if not status:
            ctx.database.session.rollback()
            ctx.logger.warning(message)
            return flask.Response(message, status=443)
        else:
            ctx.logger.info(message)

        ctx.database.session.commit()
        return flask.Response(message, status=200)

    except Exception as error:
        ctx.database.session.rollback()
        ctx.logger.warning(f"error while completing transaction: {error}")
        return flask.Response(f"incorrect input", status=443)


@Blueprints.transactions.route("/transaction/view/current", methods=["POST"])
@function_context
def view_proposal(ctx: AppContext, payload: Optional[Dict[str, str]] = None):
    if payload is None:
        payload = flask.request

    if "user" not in payload:
        return flask.Response("user field is missing", status=443)
    user = int(payload["user"])

    proposals = ctx.database.session.execute(
        orm
        .select(Transaction, Product)
        .filter(orm.and_(Transaction.status == Status.CREATED, Transaction.customer_bank_account_id == user))
        .join(Product, Product.id == Transaction.product_id)
    ).all()

    response = []
    for transaction, product in proposals:
        response.append(
            {
                "transaction_id": transaction.id,
                "amount": transaction.amount,
                "count": transaction.count,
                "product": product.name,
                "second_side": transaction.seller_bank_account_id,
            }
        )
    return flask.Response(json.dumps(response, indent=4, sort_keys=True), status=200)


@Blueprints.transactions.route("/transaction/view/history", methods=["POST"])
@function_context
def view_proposal_history(ctx: AppContext, payload: dict[str, str] | None = None):
    if payload is None:
        payload = flask.request

    if "user" not in payload:
        return flask.Response("user field is missing", status=443)
    user = int(payload["user"])

    seller_proposals = get_transactions_for(user, True)
    customer_proposals = get_transactions_for(user, False)

    response = []
    for proposals, side in [(seller_proposals, "seller"), (customer_proposals, "customer")]:
        for transaction, product in proposals:
            response.append(
                {
                    "transaction_id": transaction.id,
                    "amount": transaction.amount,
                    "count": transaction.count,
                    "product": product.name,
                    "status": transaction.status,
                    "updated_at": transaction.local_updated_at.strftime("%d/%m/%Y %H:%M:%S"),
                    "side": side,
                    "second_side": transaction.customer_bank_account_id if side == "seller" else transaction.seller_bank_account_id,
                    "is_money": product.id == 1,
                }
            )
    return flask.Response(
        json.dumps(
            sorted(response, key=lambda el: datetime.datetime.strptime(el["updated_at"], "%d/%m/%Y %H:%M:%S"), reverse=True), indent=4, sort_keys=True
        ),
        status=200,
    )


@Blueprints.transactions.route("/transaction/decide", methods=["POST"])
@function_context
def decide_on_proposal(ctx: AppContext, payload: dict[str, str] | None = None):
    if payload is None:
        payload = flask.request

    if "status" not in payload:
        return flask.Response("status field is missing", status=443)

    if "transaction_id" not in payload:
        return flask.Response("status field is missing", status=443)

    status = payload["status"]
    id = int(payload["transaction_id"])
    message, result = complete_transaction(id, status)

    ctx.logger.info(f"transaction {id} with status = {status}; completed: {result}; decision: {message}")

    if not result:
        return flask.Response(message, status=400)
    return flask.Response(message, status=200)
