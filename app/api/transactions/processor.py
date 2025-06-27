import sqlalchemy as orm

from typing import Tuple

from app.context import AppContext, function_context
from app.models import Product2BankAccount, Transaction, TransactionStatus
from app.codegen.transaction import (
	DecideTransactionResponse,
    DecideTransactionResponseStatus
)


def get_products(ctx: AppContext, account: int, product_id: int) -> Product2BankAccount:
    return ctx.database.session.execute(
        orm.select(Product2BankAccount).filter(
            orm.and_(
                Product2BankAccount.bank_account_id == account,
                Product2BankAccount.product_id == product_id
            )
        )
    ).first()


@function_context
def process(ctx: AppContext, transaction: Transaction, approved: bool) -> DecideTransactionResponse:
    if transaction.status != TransactionStatus.CREATED:
        return DecideTransactionResponse(
            DecideTransactionResponseStatus.ALREADY_PROCESSED
        )

    if not approved:
        transaction.status = TransactionStatus.REJECTED
        return DecideTransactionResponse(
            DecideTransactionResponseStatus.REJECTED
        )

    customer_wallet = get_products(ctx, transaction.customer_bank_account_id, 1)
    seller_wallet = get_products(ctx, transaction.seller_bank_account_id, 1)
    customer_products = get_products(transaction, transaction.customer_bank_account_id, transaction.product_id)
    seller_products = get_products(transaction, transaction.seller_bank_account_id, transaction.product_id)

    if transaction.amount <= 0:
        return DecideTransactionResponse(
            DecideTransactionResponseStatus.AMOUNT_OUT_OF_BOUNDS
        )
    if transaction.count <= 0:
        DecideTransactionResponse(
            DecideTransactionResponseStatus.COUNT_OUT_OF_BOUNDS
        )

    if transaction.product_id == 1:
        if seller_wallet.count < transaction.count:
            return DecideTransactionResponse(
                DecideTransactionResponseStatus.SELLER_MISSING_GOODS
            )
        customer_wallet.count += transaction.amount
        seller_wallet.count -= transaction.amount
        transaction.status = TransactionStatus.APPROVED

        return DecideTransactionResponse(
            DecideTransactionResponseStatus.ACCEPTED
        )

    if seller_products is None:
        return DecideTransactionResponse(
            DecideTransactionResponseStatus.SELLER_MISSING_GOODS
        )

    if customer_products is None:
        # create customer's relation if does not exist
        customer_products = Product2BankAccount(transaction.customer_bank_account_id, transaction.product_id, 0)
        ctx.database.session.add(customer_products)

    if customer_wallet.count < transaction.amount:
        return DecideTransactionResponse(
            DecideTransactionResponseStatus.CUSTOMER_MISSING_MONEY
        )

    if seller_products.count < transaction.count:
        return DecideTransactionResponse(
            DecideTransactionResponseStatus.SELLER_MISSING_GOODS
        )

    customer_wallet.count -= transaction.amount
    customer_products.count += transaction.count
    seller_wallet.count += transaction.amount
    seller_products.count -= transaction.count
    transaction.status = TransactionStatus.APPROVED

    return DecideTransactionResponse(
        DecideTransactionResponseStatus.ACCEPTED
    )


@function_context
def complete_transaction(ctx: AppContext, transaction_id: int, with_status: str) -> DecideTransactionResponse:
    transaction = ctx.database.session.get(Transaction, transaction_id)
    if not transaction:
        raise ValueError

    status = process(with_status == TransactionStatus.APPROVED)
    if not status:
        ctx.database.session.rollback()
        ctx.logger.warning(f"failed to complete transaction {transaction_id}: status {status}")

    ctx.database.session.session.commit()
    return status
