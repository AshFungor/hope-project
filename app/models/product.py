import sqlalchemy
import sqlalchemy.orm

import app.modules.database.handlers as database


class Product(database.ModelBase):
    __tablename__ = 'product'

    id: sqlalchemy.orm.Mapped[database.serial]
    category: sqlalchemy.orm.Mapped[database.variable_strings[64]]
    name: sqlalchemy.orm.Mapped[database.variable_strings[64]]
    level: sqlalchemy.orm.Mapped[database.small_int]


class Consumption(database.ModelBase):
    __tablename__ = 'consumption'

    id: sqlalchemy.orm.Mapped[database.serial]
    bank_account_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('bank_account.id'))
    product_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('product.id'))
    count: sqlalchemy.orm.Mapped[database.long_int]
    consumed_at: sqlalchemy.orm.Mapped[database.c_datetime]

