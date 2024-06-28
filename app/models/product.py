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

    @staticmethod
    def get_all() -> list[str]:
        return [product.name for product in env.db.impl().session.execute(
            orm.select(models.Product)
        ).scalars().all()]


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
        self.bank_account_id = validators.IntValidator.validate(bank_account_id, 64, False)
        self.product_id = validators.IntValidator.validate(product_id, 64, False)
        self.count = validators.IntValidator.validate(count, 64, False)
        self.consumed_at = validators.DtValidator.validate(consumed_at)

    @functools.cached_property
    def local_consumed_at(self):
        return self.consumed_at.astimezone(tz=validators.CurrentTimezone)

    @staticmethod
    def did_consume_enough(
        id: int,
        product_category: str, 
        norm: int, 
        time_offset: datetime.timedelta = datetime.timedelta(days=1)
    ) -> typing.Tuple[bool, str] | typing.Tuple[bool, int]:
        suitable_products = env.db.impl().session.execute(
            orm.select(models.Product) \
            .filter(
                models.Product.category == product_category
            )
        ).scalars().all()

        suitable_products = [product.id for product in suitable_products]

        consumed = env.db.impl().session.execute(
            orm.select(models.Consumption) \
            .filter(
                orm.and_(
                    models.Consumption.bank_account_id == id,
                    models.Consumption.product_id.in_(suitable_products)
                )
            )
        ).scalars().all()

        if consumed is None:
            return False, f'в этот день категория {product_category} не употреблялся'
        
        total = 0
        for entry in consumed:
            if (entry.local_consumed_at + time_offset).date() >= datetime.datetime.now(tz=validators.CurrentTimezone).date():
                total += entry.count

        if total < norm:
            return False, norm - total
        return True, 0
