import enum
import typing
import datetime

from app.env import env

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import ForeignKey

from app.modules.database.handlers import serial
from app.modules.database.handlers import long_int
from app.modules.database.handlers import c_datetime
from app.modules.database.handlers import variable_strings
from app.modules.database.handlers import ModelBase

import sqlalchemy as orm
import app.models.bank_account as bank_account
import app.modules.database.validators as validators


class Status(enum.StrEnum):
    CREATED = 'created'
    APPROVED = 'approved'
    REJECTED = 'rejected'


class Transaction(ModelBase):
    __tablename__ = 'transaction'

    id: Mapped[serial]
    product_id: Mapped[long_int] = mapped_column(ForeignKey('product.id'))
    customer_bank_account_id: Mapped[long_int] = mapped_column(ForeignKey('bank_account.id'))
    seller_bank_account_id: Mapped[long_int] = mapped_column(ForeignKey('bank_account.id'))
    count: Mapped[long_int]
    amount: Mapped[long_int]
    status: Mapped[variable_strings[32]]
    created_at: Mapped[c_datetime]
    updated_at: Mapped[c_datetime] = mapped_column(nullable=True)
    comment: Mapped[variable_strings[256]] = mapped_column(nullable=True)

    def __init__(self,
        product_id: int,                # target product for transaction
        customer_bank_account_id: int,  # customer's account
        seller_bank_account_id: int,    # seller's account
        count: int,                     # number of products
        amount: int,                    # money
        status: str | Status,           # transaction status
        created_at: datetime.datetime,  # creation time
        updated_at: datetime.datetime,  # ???
        comment: str | None             # our data
    ) -> None:
        self.product_id = product_id
        self.customer_bank_account_id = validators.IntValidator.validate(customer_bank_account_id, 64, True)
        self.seller_bank_account_id = validators.IntValidator.validate(seller_bank_account_id, 64, True)
        self.count = validators.IntValidator.validate(count, 64, True)
        self.amount = validators.IntValidator.validate(amount, 64, True)
        self.status = validators.EnumValidator.validate(status, Status, 'rejected')
        self.created_at = validators.DtValidator.validate(created_at)
        self.updated_at = validators.DtValidator.validate(updated_at)
        self.comment = validators.GenericTextValidator.validate(self._generate_comment(comment), 256, False) 

    def _generate_comment(self, additional_message: str | None) -> None:
        if additional_message is None:
            return ''
        return f'transaction comment {additional_message}'
    
    def _get_products_for(self, account: int) -> typing.Tuple[bank_account.Product2BankAccount, bank_account.Product2BankAccount] | str:
        query = None
        try:
            query = env.db.impl().session.query(bank_account.Product2BankAccount).filter(
                orm.and_(
                    bank_account.Product2BankAccount.bank_account_id == account,
                    orm.or_(
                        bank_account.Product2BankAccount.product_id == 1, # money
                        bank_account.Product2BankAccount.product_id == self.product_id
                    )
                )
            )                                                               \
            .order_by(bank_account.Product2BankAccount.product_id)          \
            .all()
        except Exception as error:
            return f'error getting products for user {account}; looked up {self.product_id} and 1 (money); error {error}'
        
        if query is None or len(query) > 2:
            if not query:
                return f'error getting products for user {account}; looked up {self.product_id} and 1 (money); empty query'
            # might happen...
            return f'error getting products for user {account}; looked up {self.product_id} and 1 (money); query returned more than 2 entries'

        return list(query) + [None for _ in range(max(0, 2 - len(query)))]
    
    def process(self, approved: bool) -> typing.Tuple[str, bool]:
        if self.status != 'created':
            return 'transaction is already processed', False
        
        if not approved:
            self.status = Status.REJECTED
            return 'transaction is rejected', True
        
        customer = self._get_products_for(self.customer_bank_account_id)
        seller = self._get_products_for(self.seller_bank_account_id)

        if isinstance(customer, str) or isinstance(seller, str):
            if isinstance(customer, str):
                return customer, False
            return seller, False

        customer_wallet, customer_products = customer
        seller_wallet, seller_products = seller

        if self.product_id == 1:
            # we make money transaction
            if seller_wallet is None or customer_wallet is None:
                return 'database lacks money entity with id = 1', False
            if seller_wallet.count < self.count:
                return 'transaction is unavailable: not enough money owned by seller', False
            customer_wallet.count += self.amount
            seller_wallet.count -= self.amount
            self.status = Status.APPROVED

            return 'transaction accepted', True

        if customer_products is None:
            try:
                # create customer's relation if does not exist
                customer_products = bank_account.Product2BankAccount(self.customer_bank_account_id, self.product_id, 0)
                env.db.impl().session.add(customer_products)
            except Exception as error:
                return f'failed to create product account with id {self.product_id} for user {self.customer_bank_account_id}; error {error}', False

        if customer_wallet.count < self.amount:
            return 'transaction is unavailable: not enough money owned by customer', False
        
        if seller_products.count < self.count:
            if self.product_id == 1:
                return 'transaction is unavailable: not enough money owned by seller', False
            return 'transaction is unavailable: not enough products owned by seller', False
        
        customer_wallet.count -= self.amount
        customer_products.count += self.count
        seller_wallet.count += self.amount
        seller_products.count -= self.count
        self.status = Status.APPROVED

        return 'transaction accepted', True
