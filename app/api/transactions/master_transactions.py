from datetime import datetime

import sqlalchemy as orm
from flask_login import login_required, current_user

from app.models.queries import wrap_crud_context
from app.models import BankAccount, Product, Transaction, TransactionStatus, Product2BankAccount

from app.codegen.types import TransactionStatusReason

from app.api import Blueprints
from app.context import AppContext
from app.api.helpers import protobufify, pythonify

from app.codegen.hope import Response
from app.api.transactions.processor import get_products
from app.api.transactions.transaction import make_status

from app.codegen.transaction import (
    MasterRemoveMoneyRequest,
    MasterAddMoneyRequest,
    MasterAddProductRequest,
    MasterRemoveProductRequest,
)


@Blueprints.transactions.route("/api/transaction/master/remove_money", methods=["POST"])
@login_required
@pythonify(MasterRemoveMoneyRequest)
def master_remove_money(ctx: AppContext, req: MasterRemoveMoneyRequest):
    customer_account = ctx.database.session.get(BankAccount, req.customer_bank_account_id)
    if not customer_account:
        return protobufify(Response(create_money_transaction=make_status(TransactionStatusReason.CUSTOMER_MISSING)))

    with wrap_crud_context():
        if req.amount <= 0:
            return protobufify(Response(create_money_transaction=make_status(TransactionStatusReason.AMOUNT_OUT_OF_BOUNDS)))

        wallet = get_products(ctx, req.customer_bank_account_id, ctx.config.money_product_id)
        if not wallet:
            wallet = Product2BankAccount(
                bank_account_id=req.customer_bank_account_id,
                product_id=ctx.config.money_product_id,
                count=0,
            )
            ctx.database.session.add(wallet)

        if wallet.count < abs(req.amount):
            return protobufify(Response(create_money_transaction=make_status(TransactionStatusReason.CUSTOMER_MISSING_MONEY)))

        tx = Transaction(
            ctx.config.money_product_id,
            req.customer_bank_account_id,
            current_user.bank_account_id,
            -abs(req.amount),
            -abs(req.amount),
            TransactionStatus.ACCEPTED,
            datetime.now(),
            datetime.now(),
            "master: remove money",
        )

        wallet.count -= abs(req.amount)

        ctx.database.session.add(tx)
        ctx.database.session.commit()

    return protobufify(Response(create_money_transaction=make_status(TransactionStatusReason.OK)))



@Blueprints.transactions.route("/api/transaction/master/add_money", methods=["POST"])
@login_required
@pythonify(MasterAddMoneyRequest)
def master_add_money(ctx: AppContext, req: MasterAddMoneyRequest):
    if not ctx.database.session.get(BankAccount, req.customer_bank_account_id):
        return protobufify(Response(create_money_transaction=make_status(TransactionStatusReason.CUSTOMER_MISSING)))

    with wrap_crud_context():
        tx = Transaction(
            ctx.config.money_product_id,
            req.customer_bank_account_id,
            current_user.bank_account_id,
            abs(req.amount),
            abs(req.amount),
            TransactionStatus.ACCEPTED,
            datetime.now(),
            datetime.now(),
            "master: add money",
        )

        wallet = get_products(ctx, req.customer_bank_account_id, ctx.config.money_product_id)
        if not wallet:
            wallet = Product2BankAccount(
                bank_account_id=req.customer_bank_account_id,
                product_id=ctx.config.money_product_id,
                count=0,
            )
            ctx.database.session.add(wallet)
        wallet.count += abs(req.amount)

        ctx.database.session.add(tx)
        ctx.database.session.commit()

    return protobufify(Response(create_money_transaction=make_status(TransactionStatusReason.OK)))


@Blueprints.transactions.route("/api/transaction/master/add_product", methods=["POST"])
@login_required
@pythonify(MasterAddProductRequest)
def master_add_product(ctx: AppContext, req: MasterAddProductRequest):
    if not ctx.database.session.get(BankAccount, req.customer_bank_account_id):
        return protobufify(Response(create_product_transaction=make_status(TransactionStatusReason.CUSTOMER_MISSING)))

    product = ctx.database.session.scalar(
        orm.select(Product).filter_by(name=req.product)
    )
    if not product:
        return protobufify(Response(create_product_transaction=make_status(TransactionStatusReason.MULTIPLE_PRODUCTS)))

    with wrap_crud_context():
        tx = Transaction(
            product.id,
            req.customer_bank_account_id,
            current_user.bank_account_id,
            abs(req.count),
            0,
            TransactionStatus.ACCEPTED,
            datetime.now(),
            datetime.now(),
            "master: add product",
        )

        wallet = get_products(ctx, req.customer_bank_account_id, product.id)
        if not wallet:
            wallet = Product2BankAccount(
                bank_account_id=req.customer_bank_account_id,
                product_id=product.id,
                count=0,
            )
            ctx.database.session.add(wallet)
        wallet.count += abs(req.count)

        ctx.database.session.add(tx)
        ctx.database.session.commit()

    return protobufify(Response(create_product_transaction=make_status(TransactionStatusReason.OK)))


@Blueprints.transactions.route("/api/transaction/master/remove_product", methods=["POST"])
@login_required
@pythonify(MasterRemoveProductRequest)
def master_remove_product(ctx: AppContext, req: MasterRemoveProductRequest):
    if not ctx.database.session.get(BankAccount, req.customer_bank_account_id):
        return protobufify(Response(create_product_transaction=make_status(TransactionStatusReason.CUSTOMER_MISSING)))

    product = ctx.database.session.scalar(
        orm.select(Product).filter_by(name=req.product)
    )
    if not product:
        return protobufify(Response(create_product_transaction=make_status(TransactionStatusReason.MULTIPLE_PRODUCTS)))

    with wrap_crud_context():
        if req.count <= 0:
            return protobufify(Response(create_product_transaction=make_status(TransactionStatusReason.COUNT_OUT_OF_BOUNDS)))

        wallet = get_products(ctx, req.customer_bank_account_id, product.id)
        if not wallet:
            wallet = Product2BankAccount(
                bank_account_id=req.customer_bank_account_id,
                product_id=product.id,
                count=0,
            )
            ctx.database.session.add(wallet)

        if wallet.count < abs(req.count):
            return protobufify(Response(create_product_transaction=make_status(TransactionStatusReason.SELLER_MISSING)))

        tx = Transaction(
            product.id,
            req.customer_bank_account_id,
            current_user.bank_account_id,
            -abs(req.count),
            0,
            TransactionStatus.ACCEPTED,
            datetime.now(),
            datetime.now(),
            "master: remove product",
        )

        wallet.count -= abs(req.count)

        ctx.database.session.add(tx)
        ctx.database.session.commit()

    return protobufify(Response(create_product_transaction=make_status(TransactionStatusReason.OK)))
