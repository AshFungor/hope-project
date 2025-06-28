from datetime import datetime

import sqlalchemy as orm
from flask_login import login_required

from app.api import Blueprints
from app.api.helpers import pythonify, protobufify, local_datetime

from app.api.transactions.processor import complete_transaction, Processor
from app.context import AppContext
from app.models import Product, Transaction, TransactionStatus
from app.models.queries import wrap_crud_context

from app.codegen.transaction import (
    CreateProductTransactionRequest,
    CreateMoneyTransactionRequest,
    ViewTransactionsRequest,
    ViewTransactionsResponse,
    CurrentTransactionsRequest,
    CurrentTransactionsResponse,
    DecideOnTransactionRequest,
)
from app.codegen.hope import Response as APIResponse
from app.codegen.types import Transaction as EntryProto
from app.codegen.types import TransactionStatusReason, TransactionStatus as TxStatus
from app.codegen.transaction import CreateTransactionResponse


@Blueprints.transactions.route("/api/transaction/product/create", methods=["POST"])
@login_required
@pythonify(CreateProductTransactionRequest)
def new_proposal(ctx: AppContext, req: CreateProductTransactionRequest):
    products = ctx.database.session.scalars(
        orm.select(Product).filter_by(name=req.product)
    ).all()

    if len(products) != 1:
        return protobufify(APIResponse(
            create_transaction=_status_response(TransactionStatusReason.MULTIPLE_PRODUCTS)
        ))

    product = products[0]
    with wrap_crud_context():
        tx = Transaction(
            product.id,
            req.customer_account,
            req.seller_account,
            req.count,
            req.amount,
            TransactionStatus.CREATED,
            datetime.now(),
            datetime.now(),
            "",
        )

        if (status := Processor.check_seller_not_customer(tx)) != TransactionStatusReason.OK:
            return protobufify(APIResponse(create_transaction=_status_response(status)))

        if (status := Processor.check_bounds(tx)) != TransactionStatusReason.OK:
            return protobufify(APIResponse(create_transaction=_status_response(status)))

        if (status := Processor.check_seller_exists(ctx, tx)) != TransactionStatusReason.OK:
            return protobufify(APIResponse(create_transaction=_status_response(status)))

        if (status := Processor.check_customer_exists(ctx, tx)) != TransactionStatusReason.OK:
            return protobufify(APIResponse(create_transaction=_status_response(status)))

        ctx.database.session.add(tx)
        ctx.database.session.commit()

    return protobufify(APIResponse(
        create_transaction=_status_response(TransactionStatusReason.OK)
    ))


@Blueprints.transactions.route("/api/transaction/money/create", methods=["POST"])
@login_required
@pythonify(CreateMoneyTransactionRequest)
def new_money_proposal(ctx: AppContext, req: CreateMoneyTransactionRequest):
    with wrap_crud_context():
        tx = Transaction(
            1,  # pseudo product id for money
            req.customer_account,
            req.seller_account,
            req.amount,
            req.amount,
            TransactionStatus.CREATED,
            datetime.now(),
            datetime.now(),
            "",
        )

        result = Processor.process(ctx, tx, approved=True)
        if result != TransactionStatusReason.OK:
            return protobufify(APIResponse(create_transaction=_status_response(result)))

        ctx.database.session.add(tx)
        ctx.database.session.commit()
        return protobufify(APIResponse(
            create_transaction=_status_response(TransactionStatusReason.OK)
        ))


@Blueprints.transactions.route("/api/transaction/current", methods=["POST"])
@login_required
@pythonify(CurrentTransactionsRequest)
def active_proposals(ctx: AppContext, req: CurrentTransactionsRequest):
    entries = ctx.database.session.execute(
        orm.select(Transaction, Product)
        .filter(
            orm.and_(
                Transaction.status == TransactionStatus.CREATED,
                Transaction.customer_bank_account_id == req.account,
            )
        )
        .join(Product, Product.id == Transaction.product_id)
    ).all()

    return protobufify(APIResponse(
        current_transactions=CurrentTransactionsResponse(
            transactions=[
                EntryProto(
                    transaction_id=tx.id,
                    amount=tx.amount,
                    count=tx.count,
                    product=product.name,
                    seller_account=tx.seller_bank_account_id,
                )
                for tx, product in entries
            ]
        )
    ))


@Blueprints.transactions.route("/api/transaction/history", methods=["POST"])
@pythonify(ViewTransactionsRequest)
def view_proposal_history(ctx: AppContext, req: ViewTransactionsRequest):
    def fetch(for_seller: bool):
        column = Transaction.seller_bank_account_id if for_seller else Transaction.customer_bank_account_id
        return ctx.database.session.execute(
            orm.select(Transaction, Product)
            .filter(column == req.account)
            .join(Product, Product.id == Transaction.product_id)
        ).all()

    response = []
    for group, role in [(fetch(True), "seller"), (fetch(False), "customer")]:
        for tx, product in group:
            response.append(
                EntryProto(
                    transaction_id=tx.id,
                    amount=tx.amount,
                    count=tx.count,
                    product=product.name,
                    status=TxStatus.from_string(tx.status.upper()),
                    updated_at=local_datetime(ctx, tx.updated_at).isoformat(),
                    side=role,
                    is_money=(product.id == 1),
                )
            )

    response.sort(key=lambda e: datetime.fromisoformat(e.updated_at), reverse=True)
    return protobufify(APIResponse(
        view_transaction_history=ViewTransactionsResponse(
            transactions=response
        )
    ))


@Blueprints.transactions.route("/api/transaction/decide", methods=["POST"])
@login_required
@pythonify(DecideOnTransactionRequest)
def decide_on_proposal(ctx: AppContext, req: DecideOnTransactionRequest):
    result = complete_transaction(req.account, req.status)
    ctx.logger.info(f"transaction {req.account} decision={req.status}: {result}")

    return protobufify(APIResponse(
        decide_on_transaction=result
    ))


def _status_response(status: TransactionStatusReason):
    return CreateTransactionResponse(status=status)
