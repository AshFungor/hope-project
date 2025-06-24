from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.database import Datetime, Ints, ModelBase, VarStrings


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

    # @staticmethod
    # def did_consume_enough(
    #     id: int, product_category: str, norm: int, time_offset: datetime.timedelta = datetime.timedelta(days=1)
    # ) -> typing.Tuple[bool, str] | typing.Tuple[bool, int]:
    #     suitable_products = env.db.impl().session.execute(orm.select(Product).filter(Product.category == product_category)).scalars().all()

    #     suitable_products = [product.id for product in suitable_products]

    #     consumed = (
    #         env.db.impl()
    #         .session.execute(
    #             orm.select(Consumption).filter(orm.and_(Consumption.bank_account_id == id, Consumption.product_id.in_(suitable_products)))
    #         )
    #         .scalars()
    #         .all()
    #     )

    #     if consumed is None:
    #         return False, f"в этот день категория {product_category} не употреблялся"

    #     total = 0
    #     for entry in consumed:
    #         if (entry.local_consumed_at + time_offset).date() > datetime.datetime.now(tz=validators.CurrentTimezone).date():
    #             total += entry.count

    #     if total < norm:
    #         return False, norm - total
    #     return True, 0
