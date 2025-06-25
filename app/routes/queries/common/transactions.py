import sqlalchemy as orm

from typing import Tuple, Union

from app.models import Product2BankAccount, Transaction
from app.models import Status
from app.context import function_context, AppContext


@function_context
def get_products_for(ctx: AppContext, transaction: Transaction, account: int) -> Union[Tuple[Product2BankAccount, Product2BankAccount], str]:
    try:
        query = ctx.database.session.execute(
            orm
            .select(Product2BankAccount)
            .filter(
                orm.and_(
                    Product2BankAccount.bank_account_id == account,
                    orm.or_(
                        Product2BankAccount.product_id == 1, # money
                        Product2BankAccount.product_id == transaction.product_id
                    ),
                )
            )
            .order_by(Product2BankAccount.product_id)
        ).all()

    except Exception as error:
        return f"error getting products ({transaction.product_id}, 1) for user {account}: {error}"

    if not query:
        return f"error getting products ({transaction.product_id}, 1) for user {account}: empty query"

    if len(query) > 2:
        return f"error getting products ({transaction.product_id}, 1) for user {account}; query returned more than 2 entries"

    return list(query) + [None for _ in range(max(0, 2 - len(query)))]

@function_context
def process(ctx: AppContext, transaction: Transaction, approved: bool) -> Tuple[str, bool]:
    if transaction.status != Status.CREATED:
        return "transaction is already processed", False

    if not approved:
        transaction.status = Status.REJECTED
        return "transaction is rejected", True

    customer = get_products_for(transaction, transaction.customer_bank_account_id)
    seller = get_products_for(transaction, transaction.seller_bank_account_id)

    if isinstance(customer, str) or isinstance(seller, str):
        if isinstance(customer, str):
            return customer, False
        return seller, False

    customer_wallet, customer_products = customer
    seller_wallet, seller_products = seller

    if transaction.amount <= 0:
        return "cannot accept transaction with negative amount", False
    if transaction.count <= 0:
        return "cannot accept transaction with negative count", False

    if transaction.product_id == 1:
        # we make money transaction
        if seller_wallet is None or customer_wallet is None:
            return "database lacks money entity with id = 1", False
        if seller_wallet.count < transaction.count:
            return "transaction is unavailable: not enough money owned by seller", False
        customer_wallet.count += transaction.amount
        seller_wallet.count -= transaction.amount
        transaction.status = Status.APPROVED

        return "transaction accepted", True

    if seller_products is None:
        return f"Seller has no products associated with this account: {transaction.seller_bank_account_id}", False

    if customer_products is None:
        try:
            # create customer's relation if does not exist
            customer_products = Product2BankAccount(transaction.customer_bank_account_id, transaction.product_id, 0)
            ctx.database.session.add(customer_products)
        except Exception as error:
            return f"failed to create product account with id {transaction.product_id} for user {transaction.customer_bank_account_id}; error {error}", False

    if customer_wallet.count < transaction.amount:
        return "transaction is unavailable: not enough money owned by customer", False

    if seller_products.count < transaction.count:
        if transaction.product_id == 1:
            return "transaction is unavailable: not enough money owned by seller", False
        return "transaction is unavailable: not enough products owned by seller", False

    customer_wallet.count -= transaction.amount
    customer_products.count += transaction.count
    seller_wallet.count += transaction.amount
    seller_products.count -= transaction.count
    transaction.status = Status.APPROVED

    return "transaction accepted", True

@function_context
def complete_transaction(ctx: AppContext, transaction_id: int, with_status: str) -> Tuple[str, bool]:
    transaction = ctx.database.session.get(Transaction, transaction_id)
    if not transaction:
        return "could not find transaction", False

    message, status = process(with_status == Status.APPROVED)
    if not status:
        ctx.database.session.rollback()
        ctx.logger.warning(f"failed to complete transaction {transaction_id}: error {message}")

    ctx.database.session.session.commit()
    return message, status