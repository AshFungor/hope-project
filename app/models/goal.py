import datetime
from functools import cached_property

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.types import Datetime, Ints, ModelBase


class Goal(ModelBase):
    __tablename__ = "goal"

    id: Mapped[Ints.Serial]
    bank_account_id: Mapped[Ints.Long] = mapped_column(ForeignKey("bank_account.id"))
    created_at: Mapped[Datetime.Datetime]
    amount_on_setup: Mapped[Ints.Long] = mapped_column(nullable=True)
    value: Mapped[Ints.Long] = mapped_column(nullable=True)
    amount_on_validate: Mapped[Ints.Long] = mapped_column(nullable=True)
    complete: Mapped[bool] = mapped_column(default=False)

    def __init__(
        self,
        bank_account_id: int,
        value: int,
        amount_on_setup: int,
        amount_on_validate: int | None = None,
        created_at: datetime.datetime | None = None,
        complete: bool | None = False,
    ) -> None:
        self.bank_account_id = bank_account_id
        self.value = value
        self.amount_on_setup = amount_on_setup
        self.amount_on_validate = amount_on_validate
        if created_at is None:
            created_at = datetime.datetime.now()
        self.created_at = created_at
        self.complete = complete

    @cached_property
    def empty(self) -> bool:
        return self.value is None
