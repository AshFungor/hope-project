from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.types import Datetime, Ints, ModelBase, VarStrings


class Product(ModelBase):
    __tablename__ = "product"

    id: Mapped[Ints.Serial]
    category: Mapped[VarStrings.Char64]
    # categories: FOOD, TECHNIC, CLOTHES (goods), MINERALS (resources), ENERGY (energy)
    name: Mapped[VarStrings.Char64]
    level: Mapped[Ints.Short]

    def __init__(self, category: str, name: str, level: int):
        self.category = category
        self.name = name
        self.level = level


class Consumption(ModelBase):
    __tablename__ = "consumption"

    id: Mapped[Ints.Serial]
    bank_account_id: Mapped[Ints.Long] = mapped_column(ForeignKey("bank_account.id"))
    product_id: Mapped[Ints.Long] = mapped_column(ForeignKey("product.id"))
    count: Mapped[Ints.Long]
    consumed_at: Mapped[Datetime.Datetime]  # type:ignore

    def __init__(self, bank_account_id: int, product_id: int, count: int, consumed_at: datetime):
        self.bank_account_id = bank_account_id
        self.product_id = product_id
        self.count = count
        self.consumed_at = consumed_at
