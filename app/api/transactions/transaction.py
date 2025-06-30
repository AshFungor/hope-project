from datetime import datetime

import sqlalchemy as orm
from flask_login import login_required

from app.api import Blueprints
from app.api.helpers import local_datetime, protobufify, pythonify
from app.api.transactions.processor import Processor, complete_transaction
from app.codegen.hope import Response as APIResponse
from app.codegen.transaction import (
    CreateMoneyTransactionRequest,
    CreateProductTransactionRequest,
    CreateTransactionResponse,
    CurrentTransactionsRequest,
    CurrentTransactionsResponse,
    DecideOnTransactionRequest,
    ViewTransactionsRequest,
    ViewTransactionsResponse,
)
from app.codegen.types import Transaction as EntryProto
from app.codegen.types import TransactionStatus as TxStatus
from app.codegen.types import TransactionStatusReason
from app.context import AppContext
from app.models import Product, Transaction, TransactionStatus
from app.models.queries import wrap_crud_context


def make_status(status: TransactionStatusReason):
    return CreateTransactionResponse(status=status)


@Blueprints.transactions.route("/api/transaction/product/create", methods=["POST"])
@login_required
@pythonify(CreateProductTransactionRequest)
def new_proposal(ctx: AppContext, req: CreateProductTransactionRequest):
    products = ctx.database.session.scalars(
        orm.select(Product).filter_by(name=req.product)
    ).all()

    if len(products) != 1:
        return protobufify(
            APIResponse(
                create_transaction=make_status(TransactionStatusReason.MULTIPLE_PRODUCTS)
            )
        )

    product = products[0]
    with wrap_crud_context():
        tx = Transaction(
            product.id,
            req.customer_bank_account_id,
            req.seller_bank_account_id,
            req.count,
            req.amount,
            TransactionStatus.CREATED,
            datetime.now(),
            datetime.now(),
            "",
        )

        for check in [
            Processor.check_seller_not_customer,
            Processor.check_bounds,
            Processor.check_seller_exists,
            Processor.check_customer_exists,
        ]:
            status = check(ctx, tx) if 'exists' in check.__name__ else check(tx)
            if status != TransactionStatusReason.OK:
                return protobufify(
                    APIResponse(create_transaction=make_status(status))
                )

        ctx.database.session.add(tx)
        ctx.database.session.commit()

    return protobufify(
        APIResponse(create_product_transaction=make_status(TransactionStatusReason.OK))
    )


@Blueprints.transactions.route("/api/transaction/money/create", methods=["POST"])
@login_required
@pythonify(CreateMoneyTransactionRequest)
def new_money_proposal(ctx: AppContext, req: CreateMoneyTransactionRequest):
    with wrap_crud_context():
        tx = Transaction(
            ctx.config.money_product_id,
            req.customer_bank_account_id,
            req.seller_bank_account_id,
            req.amount,
            req.amount,
            TransactionStatus.CREATED,
            datetime.now(),
            datetime.now(),
            "",
        )

        result = Processor.process(ctx, tx, approved=True)
        if result != TransactionStatusReason.OK:
            return protobufify(
                APIResponse(create_transaction=make_status(result))
            )

        ctx.database.session.add(tx)
        ctx.database.session.commit()
        return protobufify(
            APIResponse(create_money_transaction=make_status(TransactionStatusReason.OK))
        )


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

    return protobufify(
        APIResponse(
            current_transactions=CurrentTransactionsResponse(
                transactions=[
                    EntryProto(
                        transaction_id=tx.id,
                        amount=tx.amount,
                        count=tx.count,
                        product=product.name,
                        seller_bank_account_id=tx.seller_bank_account_id,
                    )
                    for tx, product in entries
                ]
            )
        )
    )


@Blueprints.transactions.route("/api/transaction/history", methods=["POST"])
@login_required
@pythonify(ViewTransactionsRequest)
def view_proposal_history(ctx: AppContext, req: ViewTransactionsRequest):
    def fetch(for_seller: bool):
        column = Transaction.seller_bank_account_id if for_seller else Transaction.customer_bank_account_id
        return ctx.database.session.execute(
            orm.select(Transaction, Product)
            .filter(column == req.account)
            .join(Product, Product.id == Transaction.product_id)
        ).all()

    str_format = "%Y-%m-%d %H:%M"
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
                    updated_at=local_datetime(ctx, tx.updated_at).strftime(str_format),
                    side=role,
                    is_money=(product.id == ctx.config.money_product_id),
                )
            )

    response.sort(
        key=lambda e: datetime.strptime(e.updated_at, str_format), reverse=True
    )
    return protobufify(
        APIResponse(
            view_transaction_history=ViewTransactionsResponse(transactions=response)
        )
    )


@Blueprints.transactions.route("/api/transaction/decide", methods=["POST"])
@login_required
@pythonify(DecideOnTransactionRequest)
def decide_on_proposal(ctx: AppContext, req: DecideOnTransactionRequest):
    result = complete_transaction(req.id, req.status)
    ctx.logger.info(f"transaction {req.id} decision={req.status}: {result}")

    return protobufify(APIResponse(decide_on_transaction=result))
