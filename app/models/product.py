import typing
import datetime
import functools

import sqlalchemy as orm

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import ForeignKey

from app.modules.database.handlers import serial
from app.modules.database.handlers import long_int
from app.modules.database.handlers import c_datetime
from app.modules.database.handlers import variable_strings
from app.modules.database.handlers import small_int
from app.modules.database.handlers import ModelBase

import app.modules.database.validators as validators
import app.models as models

from app.env import env


class Product(ModelBase):
    __tablename__ = 'product'

    id: Mapped[serial]
    category: Mapped[variable_strings[64]]
    # категории: FOOD, TECHNIC, CLOTHES (товары), MINERALS (ресурсы), ENERGY (энергия)
    name: Mapped[variable_strings[64]]
    level: Mapped[small_int]

    def __init__(
        self,
        category: str,
        name: str,
        level: int
    ) -> None:
        self.category = validators.GenericTextValidator.validate(category, 64, False)
        self.name = validators.GenericTextValidator.validate(name, 64, False)
        self.level = validators.IntValidator.validate(level, 16, True)


class Consumption(ModelBase):
    __tablename__ = 'consumption'

    id: Mapped[serial]
    bank_account_id: Mapped[long_int] = mapped_column(ForeignKey('bank_account.id'))
    product_id: Mapped[long_int] = mapped_column(ForeignKey('product.id'))
    count: Mapped[long_int]
    consumed_at: Mapped[c_datetime]

    def __init__(
        self,
        bank_account_id: int,
        product_id: int,
        count: int,
        consumed_at: datetime.datetime
    ):
        self.bank_account_id = validators.IntegerValidator.validate(bank_account_id, 64, False)
        self.product_id = validators.IntegerValidator.validate(product_id, 64, False)
        self.count = validators.IntegerValidator.validate(count, 64, False)
        self.consumed_at = validators.DtValidator.validate(consumed_at)

    @functools.cached_property
    def local_consumed_at(self):
        return self.consumed_at.astimezone(tz=validators.CurrentTimezone)

    @staticmethod
    def did_consume_enough(
        id: int, 
        product_id: int, 
        product_name: str, 
        norm: int, 
        limitByCurrentDay: bool = False
    ) -> typing.Tuple[bool, str] | typing.Tuple[bool, int]:
        consumed = env.db.impl().session.execute(
            orm.select(models.Consumption) \
            .filter(
                orm.and_(
                    models.Consumption.bank_account_id == id,
                    models.Consumption.product_id == product_id
                )
            ).join(
                models.Product, models.Product.id == models.Consumption.product_id
            )
        ).all()

        if consumed is None:
            return False, f'в этот день товар {product_name} не употреблялся'
        
        total = 0
        for entry in consumed:
            if limitByCurrentDay and entry.local_consumed_at.date() > datetime.datetime.now(tz=validators.CurrentTimezone).date():
                total += entry.count

        if total < norm:
            return False, norm - total
        return True, 0
