import datetime
import flask
import json

import sqlalchemy as orm

from http import HTTPStatus
from flask import request, jsonify
from typing import List
from flask_login import login_required

from app.api import Blueprints
from app.models.queries import wrap_crud_call
from app.models import Transaction, Product, User, Company, TransactionStatus
from app.api.transactions.processor import process, complete_transaction
from app.context import function_context, AppContext


@Blueprints.transactions.route("/api/transaction/product/create", methods=["POST"])
@login_required
@function_context
def new_proposal(ctx: AppContext):
    try:
        seller_account = int(request.json["seller_account"]) 
        customer_account = int(request.json["customer_account"])
        product_name = request.json["product"]
        count = int(request.json["count"])
        amount = int(request.json["amount"])
    except (ValueError, KeyError):
        return "Parameters are missing or their types are mismatched", HTTPStatus.BAD_REQUEST
    
    product = ctx.database.session.execute(
        orm.select(Product).filter_by(Product.name == product_name)
    ).all()

    if len(product) != 1:
        return f"Could not resolve product name: {product_name}", HTTPStatus.BAD_REQUEST
        
    @wrap_crud_call
    def __create():
        transaction = Transaction(
            product.id,
            int(customer_account),
            int(seller_account),
            int(count),
            int(amount),
            TransactionStatus.CREATED,
            datetime.datetime.now(),
            datetime.datetime.now(),
            "",
        )
        ctx.database.session.add(transaction)
        ctx.database.session.commit()

    __create()
    return "proposal created", HTTPStatus.OK


@Blueprints.transactions.route("/api/transaction/money/create", methods=["POST"])
@login_required
@function_context
def new_money_proposal(ctx: AppContext) -> flask.Response:
    try:
        seller_account = int(request.json["seller_account"]) 
        customer_account = int(request.json["customer_account"])
        amount = int(request.json["amount"])
    except (ValueError, KeyError):
        return "Parameters are missing or their types are mismatched", HTTPStatus.BAD_REQUEST

    @wrap_crud_call
    def __create():
        transaction = Transaction(
            1,
            int(customer_account),
            int(seller_account),
            int(amount),
            int(amount),
            TransactionStatus.CREATED,
            datetime.datetime.now(),
            datetime.datetime.now(),
            "",
        )
        ctx.database.session.add(transaction)
        message, status = process(transaction, True)

        if not status:
            ctx.logger.warning(message)
            return "could add money transaction", HTTPStatus.BAD_REQUEST
        
        return "Transaction added", HTTPStatus.OK
    
    retval = __create()
    if retval is not None:
        return retval
    return "Failed to process", HTTPStatus.BAD_REQUEST


@Blueprints.transactions.route("/api/transaction/view/current", methods=["POST"])
@login_required
@function_context
def active_proposals(ctx: AppContext):
    try:
        account = int(request.json["account"])
    except (ValueError, KeyError):
        return "Parameters are missing or their types are mismatched", HTTPStatus.BAD_REQUEST

    proposals = ctx.database.session.execute(
        orm
        .select(Transaction, Product)
        .filter(orm.and_(Transaction.status == TransactionStatus.CREATED, Transaction.customer_bank_account_id == account))
        .join(Product, Product.id == Transaction.product_id)
    ).all()

    return jsonify(
        [
            {
                "transaction_id": transaction.id,
                "amount": transaction.amount,
                "count": transaction.count,
                "product": product.name,
                "second_side": transaction.seller_bank_account_id,
            } for transaction, product in proposals
        ]
    )


@Blueprints.transactions.route("/api/transaction/view/history", methods=["POST"])
@function_context
def view_proposal_history(ctx: AppContext):
    try:
        account = int(request.json["account"])
    except (ValueError, KeyError):
        return "Parameters are missing or their types are mismatched", HTTPStatus.BAD_REQUEST

    def get_transactions_for(ctx: AppContext, id: int, for_seller = True) -> List[Transaction]:
        return ctx.database.session.execute(
            orm
            .select(Transaction, Product)
            .filter((Transaction.seller_bank_account_id if for_seller else Transaction.customer_bank_account_id) == id)
            .join(Product, Product.id == Transaction.product_id)        
        ).all()

    seller_proposals = get_transactions_for(ctx, account, True)
    customer_proposals = get_transactions_for(ctx, account, False)

    response = []
    for proposals, side in [(seller_proposals, "seller"), (customer_proposals, "customer")]:
        response.extend(
            {
                "transaction_id": transaction.id,
                "amount": transaction.amount,
                "count": transaction.count,
                "product": product.name,
                "status": transaction.status,
                "updated_at": transaction.updated_at.strftime("%d/%m/%Y %H:%M:%S"),
                "side": side,
                "second_side": transaction.customer_bank_account_id if side == "seller" else transaction.seller_bank_account_id,
                "is_money": product.id == 1,
            } for transaction, product in proposals
        )

    return jsonify(
        sorted(
            response,
            key=lambda entry: datetime.datetime.strptime(entry["updated_at"], "%d/%m/%Y %H:%M:%S"), reverse=True
        ),
    )


@Blueprints.transactions.route("/api/transaction/decide", methods=["POST"])
@login_required
@function_context
def decide_on_proposal(ctx: AppContext):
    try:
        status = request.json["status"]
        transaction_id = int(request.json["account"])
    except (ValueError, KeyError):
        return "Parameters are missing or their types are mismatched", HTTPStatus.BAD_REQUEST

    message, result = complete_transaction(transaction_id, status)
    ctx.logger.info(f"transaction {id} with status = {status}; completed: {result}; decision: {message}")

    if not result:
        return message, HTTPStatus.BAD_REQUEST
    return message, HTTPStatus.OK
