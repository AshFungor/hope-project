import sqlalchemy as orm

from app.context import AppContext, function_context
from app.models import Product2BankAccount, Transaction, TransactionStatus, BankAccount
from app.codegen.transaction import DecideOnTransactionResponse
from app.codegen.types import TransactionStatusReason


class Processor:
    __ctx: AppContext = AppContext.safe_load()

    @classmethod
    def check_seller_not_customer(cls, transaction: Transaction) -> TransactionStatusReason:
        if transaction.customer_bank_account_id == transaction.seller_bank_account_id:
            return TransactionStatusReason.CUSTOMER_IS_SELLER
        return cls.ok()

    @classmethod
    def check_seller_exists(cls, ctx: AppContext, transaction: Transaction) -> TransactionStatusReason:
        if not ctx.database.session.get(BankAccount, transaction.seller_bank_account_id):
            return TransactionStatusReason.SELLER_MISSING
        return cls.ok()

    @classmethod
    def check_customer_exists(cls, ctx: AppContext, transaction: Transaction) -> TransactionStatusReason:
        if not ctx.database.session.get(BankAccount, transaction.customer_bank_account_id):
            return TransactionStatusReason.CUSTOMER_MISSING
        return cls.ok()

    @classmethod
    def check_not_processed(cls, transaction: Transaction) -> TransactionStatusReason:
        if transaction.status != TransactionStatus.CREATED:
            return TransactionStatusReason.ALREADY_PROCESSED
        return cls.ok()

    @classmethod
    def check_bounds(cls, transaction: Transaction) -> TransactionStatusReason:
        if transaction.amount <= 0:
            return TransactionStatusReason.AMOUNT_OUT_OF_BOUNDS
        if transaction.count <= 0:
            return TransactionStatusReason.COUNT_OUT_OF_BOUNDS
        return cls.ok()

    @staticmethod
    def ok() -> TransactionStatusReason:
        return TransactionStatusReason.OK

    @classmethod
    def process(cls, ctx: AppContext, transaction: Transaction, approved: bool) -> TransactionStatusReason:
        if (result := cls.check_not_processed(transaction)) != TransactionStatusReason.OK:
            return result

        if not approved:
            transaction.status = TransactionStatus.REJECTED
            return cls.ok()

        if (result := cls.check_seller_exists(ctx, transaction)) != TransactionStatusReason.OK:
            return result

        if (result := cls.check_customer_exists(ctx, transaction)) != TransactionStatusReason.OK:
            return result

        if (result := cls.check_seller_not_customer(transaction)) != TransactionStatusReason.OK:
            return result

        if (result := cls.check_bounds(transaction)) != TransactionStatusReason.OK:
            return result

        customer_wallet = get_products(ctx, transaction.customer_bank_account_id, 1)
        seller_wallet = get_products(ctx, transaction.seller_bank_account_id, 1)
        customer_products = get_products(ctx, transaction.customer_bank_account_id, transaction.product_id)
        seller_products = get_products(ctx, transaction.seller_bank_account_id, transaction.product_id)

        if transaction.product_id == 1:
            if not seller_wallet or seller_wallet.count < transaction.count:
                return TransactionStatusReason.SELLER_MISSING_GOODS
            if not customer_wallet:
                return TransactionStatusReason.CUSTOMER_MISSING_MONEY
            customer_wallet.count += transaction.amount
            seller_wallet.count -= transaction.amount

            transaction.status = TransactionStatus.ACCEPTED
            return cls.ok()

        if not seller_products or seller_products.count < transaction.count:
            return TransactionStatusReason.SELLER_MISSING_GOODS
        if not customer_wallet or customer_wallet.count < transaction.amount:
            return TransactionStatusReason.CUSTOMER_MISSING_MONEY

        if not customer_products:
            customer_products = Product2BankAccount(
                bank_account_id=transaction.customer_bank_account_id,
                product_id=transaction.product_id,
                count=0
            )
            ctx.database.session.add(customer_products)

        customer_wallet.count -= transaction.amount
        seller_wallet.count += transaction.amount
        seller_products.count -= transaction.count
        customer_products.count += transaction.count

        transaction.status = TransactionStatus.ACCEPTED
        ctx.database.session.commit()

        return cls.ok()


def get_products(ctx: AppContext, account: int, product_id: int) -> Product2BankAccount | None:
    return ctx.database.session.scalar(
        orm.select(Product2BankAccount).filter(
            orm.and_(
                Product2BankAccount.bank_account_id == account,
                Product2BankAccount.product_id == product_id,
            )
        )
    )


@function_context
def complete_transaction(ctx: AppContext, transaction_id: int, with_status: str) -> DecideOnTransactionResponse:
    transaction = ctx.database.session.get(Transaction, transaction_id)
    if not transaction:
        raise ValueError(f"Transaction {transaction_id} not found")

    result = Processor.process(ctx, transaction, with_status == TransactionStatus.ACCEPTED)

    if result != TransactionStatusReason.OK:
        ctx.database.session.rollback()
        ctx.logger.warning(f"Failed to complete transaction {transaction_id}: {result}")
    else:
        ctx.database.session.commit()

    return DecideOnTransactionResponse(status=result)
