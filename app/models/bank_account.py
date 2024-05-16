import sqlalchemy
import sqlalchemy.orm

import app.modules.database.handlers as database


class BankAccount(database.ModelBase):
    __tablename__ = 'bank_account'

    id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(primary_key=True)


class Product2BankAccount(database.ModelBase):
    __tablename__ = 'product_to_bank_account'

    bank_account_id: sqlalchemy.orm.Mapped[database.serial] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('bank_account.id'))
    product_id: sqlalchemy.orm.Mapped[database.serial] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('product.id'))
    count: sqlalchemy.orm.Mapped[database.long_int]