from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.types import Ints, ModelBase


class CityHall(ModelBase):
    __tablename__ = "city_hall"

    id: Mapped[Ints.Serial]
    bank_account_id: Mapped[Ints.Long] = mapped_column(ForeignKey("bank_account.id"))
    mayor_id: Mapped[Ints.Long] = mapped_column(ForeignKey("users.id"))
    economic_assistant_id: Mapped[Ints.Long] = mapped_column(ForeignKey("users.id"))
    social_assistant_id: Mapped[Ints.Long] = mapped_column(ForeignKey("users.id"))

    def __init__(
        self,
        bank_account_id: int,
        mayor_id: int,
        economic_assistant_id: int,
        social_assistant_id: int
    ):
        self.bank_account_id = bank_account_id
        self.mayor_id = mayor_id
        self.economic_assistant_id = economic_assistant_id
        self.social_assistant_id = social_assistant_id
