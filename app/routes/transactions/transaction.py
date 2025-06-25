import json
import math

import flask
import flask_login

import sqlalchemy as orm

from app.routes import Blueprints
from app.context import function_context, AppContext
from app.models import Product2BankAccount, Product
from app.routes.transactions.proposal import view_proposal, view_proposal_history, new_proposal, new_money_proposal


@Blueprints.proposals.route("/view_transactions", methods=["GET"])
@flask_login.login_required
@function_context
def view_transaction(ctx: AppContext):
    user_id = flask.request.args.get("account", None)
    if user_id is None:
        # get user bank account id & make payload from it
        user_id = flask_login.current_user.bank_account_id
    payload = {"user": user_id}

    response = json.loads(view_proposal(payload).data)
    return flask.render_template("account/transaction/view_transaction.html", transactions=response)


@Blueprints.proposals.route("/history", methods=["GET"])
@flask_login.login_required
@function_context
def view_history(ctx: AppContext):
    offset = max(int(flask.request.args.get("offset", 0)), 0)
    length = max(int(flask.request.args.get("length", 7)), 1)
    user_id = flask.request.args.get("account", None)

    if user_id is None:
        user_id = flask_login.current_user.bank_account_id

    payload = {"user": user_id}
    response = json.loads(view_proposal_history(payload).data)
    selected, pages = [], [
        {"offset": length * curr, "length": length, "num": curr}
        for curr in range(int(math.ceil(len(response) / length)))
    ]

    for transaction in response[offset : offset + length]:
        selected.append(transaction)

    return flask.render_template(
        "account/common/view_all_transactions.html",
        transactions=selected,
        prev_offset=max(offset - length, 0),
        prev_length=length,
        next_offset=min(len(response) // length * length, offset + length),
        next_length=length,
        pages=pages,
        id=user_id,
    )


@Blueprints.proposals.route("/new_transaction", methods=["GET"])
@flask_login.login_required
@function_context
def new_transaction(ctx: AppContext):
    user_id = flask.request.args.get("account", None)
    if user_id is None:
        user_id = flask_login.current_user.bank_account_id

    products = ctx.database.session.execute(
        orm
        .select(Product)
        .join(Product2BankAccount, Product.id == Product2BankAccount.product_id)
        .filter(Product2BankAccount.bank_account_id == user_id)
    ).all()

    data = []
    for number, product in zip(range(len(products)), products):
        data.append({"name": product.name, "number": number})

    return flask.render_template("accounts/transaction/make_transaction.html", user_bank_account=user_id, products=data)


@Blueprints.proposals.route("/new_money_transaction", methods=["GET"])
@flask_login.login_required
@function_context
def new_money_transaction(ctx: AppContext):
    user_id = flask.request.args.get("account", None)
    if user_id is None:
        user_id = flask_login.current_user.bank_account_id
    return flask.render_template("accounts/transaction/make_money_transaction.html", user_bank_account=user_id)


@Blueprints.transactions.route("/transaction/parse/create", methods=["POST"])
@function_context
def parse_new_transaction(ctx: AppContext):
    mapper = {
        "seller-account": "customer_account",
        "bank_account_id": "seller_account",
        "product-name": "product",
        "count": "product_count",
        "amount": "amount",
    }

    params = {}
    for key, value in mapper.items():
        if key not in flask.request.form:
            return flask.Response(f"missing form field: {key}", status=443)
        params[value] = flask.request.form.get(key, None)

    try:
        response = new_proposal(params)
    except Exception as error:
        ctx.logger.warning(f"service request failed in handles module: {__name__}; error: {error}")
    if response is not None and response.status_code != 200:
        ctx.logger.warning(f"message return code: {response.status_code}; message: " + response.get_data(as_text=True))

    if response.status_code == 200:
        flask.flash(response.data.decode("UTF-8"), category="success")
    else:
        flask.flash(response.data.decode("UTF-8"), category="danger")

    return flask.redirect(flask.url_for("proposal.new_transaction", account=params["seller_account"]))


@Blueprints.transactions.route("/transaction/parse/money/create", methods=["POST"])
@function_context
def parse_new_money_transaction(ctx: AppContext):
    mapper = {
        "seller-account": "customer_account",
        "bank_account_id": "seller_account",
        "amount": "amount"
    }

    params = {}
    for key, value in mapper.items():
        if key not in flask.request.form:
            return flask.Response(f"missing form field: {key}", status=443)
        params[value] = flask.request.form.get(key, None)

    try:
        response = new_money_proposal(params)
    except Exception as error:
        ctx.logger.warning(f"service request failed in handles module: {__name__}; error: {error}")
    if response is not None and response.status_code != 200:
        ctx.logger.warning(f"message return code: {response.status_code}; message: " + response.get_data(as_text=True))

    if response.status_code == 200:
        flask.flash(response.data.decode("UTF-8"), category="success")
    else:
        flask.flash(response.data.decode("UTF-8"), category="danger")
    return flask.redirect(flask.url_for("proposal.new_money_transaction", account=params["seller_account"]))
