from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import ForeignKey

from app.modules.database.handlers import serial
from app.modules.database.handlers import long_int
from app.modules.database.handlers import c_datetime
from app.modules.database.handlers import variable_strings
from app.modules.database.handlers import small_int
from app.modules.database.handlers import ModelBase


class Product(ModelBase):
    __tablename__ = 'product'

    id: Mapped[serial]
    category: Mapped[variable_strings[64]]
    name: Mapped[variable_strings[64]]
    level: Mapped[small_int]


class Consumption(ModelBase):
    __tablename__ = 'consumption'

    id: Mapped[serial]
    bank_account_id: Mapped[long_int] = mapped_column(ForeignKey('bank_account.id'))
    product_id: Mapped[long_int] = mapped_column(ForeignKey('product.id'))
    count: Mapped[long_int]
    consumed_at: Mapped[c_datetime]

