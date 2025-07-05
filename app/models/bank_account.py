from enum import IntEnum
from random import randint
from typing import Optional, Self

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.types import Ints, ModelBase


class BankAccount(ModelBase):
    """
    Bank accounts are centric entity for the game, representing
    short unique ids for any organization or person.
    """

    __tablename__ = "bank_account"

    id: Mapped[Ints.Serial] = mapped_column(primary_key=True)

    def __init__(self, id: Optional[int] = None):
        self.id = id


class Product2BankAccount(ModelBase):
    """Product to Bank Account relation table"""

    __tablename__ = "product_to_bank_account"

    bank_account_id: Mapped[Ints.Serial] = mapped_column(ForeignKey("bank_account.id"))
    product_id: Mapped[Ints.Serial] = mapped_column(ForeignKey("product.id"))
    count: Mapped[Ints.Long]

    def __init__(self, bank_account_id: int, product_id: int, count: int):
        self.bank_account_id = bank_account_id
        self.product_id = product_id
        self.count = count
