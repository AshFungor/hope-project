import enum

import sqlalchemy
import sqlalchemy.orm

import app.modules.database.handlers as database


class Status(enum.StrEnum):
    CREATED = 'created'
    APPROVED = 'approved'
    REJECTED = 'rejected'


class Transaction(database.ModelBase):
    __tablename__ = 'transaction'

    id: sqlalchemy.orm.Mapped[database.serial]
    product_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('product.id'))
    customer_bank_account_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('bank_account.id'))
    seller_bank_account_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('bank_account.id'))
    count: sqlalchemy.orm.Mapped[database.long_int]
    amount: sqlalchemy.orm.Mapped[database.long_int]
    status: sqlalchemy.orm.Mapped[database.variable_strings[32]]
    created_at: sqlalchemy.orm.Mapped[database.c_datetime]
    updated_at: sqlalchemy.orm.Mapped[database.c_datetime] = sqlalchemy.orm.mapped_column(nullable=True)
    comment: sqlalchemy.orm.Mapped[database.variable_strings[256]] = sqlalchemy.orm.mapped_column(nullable=True)

