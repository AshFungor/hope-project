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

import app.models as models
import sqlalchemy.orm as orm
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
        self.comment = validators.GenericTextValidator.validate(Transaction._generate_comment(comment), 256, False) 

    def _generate_comment(self, additional_message: str | None) -> None:
        if additional_message is None:
            return ''
        return f'transaction comment {additional_message}'
    
    def _get_products_for(self, account: int) -> typing.Tuple[models.Product2BankAccount, models.Product2BankAccount]:
        query = env.db.impl().session.query(models.Product2BankAccount).filter(
            orm.and_(
                models.Product2BankAccount.bank_account_id == account,
                orm.or_(
                    models.Product2BankAccount.product_id == 1, # money
                    models.Product2BankAccount.product_id == self.product_id
                )
            )
        )                                                       \
        .order_by(models.Product2BankAccount.product_id)        \
        .all()

        return list(query) + [None for _ in range(max(0, 2 - len(query)))]
    
    def process(self, approved: bool) -> typing.Tuple[str, bool]:
        if self.status != 'created':
            return 'transaction is already processed', False
        
        if not approved:
            self.status = Status.REJECTED
            return 'transaction is rejected', True
        
        customer_wallet, customer_products = self._get_products_for(self.customer_bank_account_id)
        seller_wallet, seller_products = self._get_products_for(self.seller_bank_account_id)

        if customer_products is None:
            # create customer's relation if does not exist
            customer_products = models.Product2BankAccount(self.customer_bank_account_id, self.product_id, 0)
            env.db.impl().session.add(customer_products)

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
        env.db.impl().session.commit()

        return 'transaction accepted', True



        


