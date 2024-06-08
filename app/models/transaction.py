import enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.database.handlers import ModelBase, serial, long_int, c_datetime, variable_strings


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
