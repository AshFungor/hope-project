from datetime import datetime

import sqlalchemy as orm
from flask_login import login_required

from app.api import Blueprints
from app.api.helpers import pythonify, protobufify
from app.context import AppContext
from app.models import Transaction, TransactionStatus, Product
from app.models.queries import wrap_crud_context

from app.api.transactions.processor import Processor

from app.codegen.transaction import (
    CreateMoneyTransactionRequest,
    CreateProductTransactionRequest,
    CreateTransactionResponse,
)
from app.codegen.types import TransactionStatusReason


def _status_response(status: TransactionStatusReason):
    return CreateTransactionResponse(status=status)


@Blueprints.master.route("/api/master/transaction/money", methods=["POST"])
@login_required
@pythonify(CreateMoneyTransactionRequest)
def master_money_transaction(ctx: AppContext, req: CreateMoneyTransactionRequest):
    with wrap_crud_context():
        tx = Transaction(
            1,
            req.customer_account,
            req.seller_account,
            req.amount,
            req.amount,
            TransactionStatus.CREATED,
            datetime.now(),
            datetime.now(),
            "",
        )

        status = Processor.process(ctx, tx, approved=True)
        if status != TransactionStatusReason.OK:
            ctx.logger.warning(f"Failed Processor: {status}")
            ctx.database.session.rollback()
            return protobufify(_status_response(status))

        ctx.database.session.add(tx)
        ctx.database.session.commit()

        return protobufify(_status_response(TransactionStatusReason.OK))


@Blueprints.master.route("/api/master/transaction/product", methods=["POST"])
@login_required
@pythonify(CreateProductTransactionRequest)
def master_product_transaction(ctx: AppContext, req: CreateProductTransactionRequest):
    product = ctx.database.session.scalar(
        orm.select(Product).filter_by(name=req.product)
    )
    if not product:
        return protobufify(_status_response(TransactionStatusReason.MULTIPLE_PRODUCTS))

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

        # Прогоняем Processor, approved=True
        status = Processor.process(ctx, tx, approved=True)
        if status != TransactionStatusReason.OK:
            ctx.logger.warning(f"Failed Processor: {status}")
            ctx.database.session.rollback()
            return protobufify(_status_response(status))

        ctx.database.session.add(tx)
        ctx.database.session.commit()

        return protobufify(_status_response(TransactionStatusReason.OK))
