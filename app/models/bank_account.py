from enum import IntEnum
from random import randint
from typing import Optional, Self

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.types import Ints, ModelBase


class BankAccount(ModelBase):
    __tablename__ = "bank_account"
    __tail_len = 4

    class AccountMapping(IntEnum):
        CITY_HALL = 1
        COMPANY = 2
        PREFECTURE = 3
        USER = 5

    id: Mapped[Ints.Serial] = mapped_column(primary_key=True)

    def __init__(self, id: Optional[int] = None):
        self.id = id

    @classmethod
    def from_kind(cls, kind: AccountMapping) -> int:
        tail = randint(10 ** cls.__tail_len, 10 ** (cls.__tail_len + 1) - 1)
        s = f"{int(kind)}{tail}"[:1 + cls.__tail_len]
        return int(s)


class Product2BankAccount(ModelBase):
    __tablename__ = "product_to_bank_account"

    bank_account_id: Mapped[Ints.Serial] = mapped_column(ForeignKey("bank_account.id"))
    product_id: Mapped[Ints.Serial] = mapped_column(ForeignKey("product.id"))
    count: Mapped[Ints.Long]

    def __init__(self, bank_account_id: int, product_id: int, count: int):
        self.bank_account_id = bank_account_id
        self.product_id = product_id
        self.count = count
