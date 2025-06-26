import datetime
import enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.types import Datetime, Ints, ModelBase, VarStrings


class Role(enum.StrEnum):
    CEO = "CEO"
    FOUNDER = "founder"
    EMPLOYEE = "employee"
    CFO = "CFO"
    MARKETING_MANAGER = "marketing_manager"
    PRODUCTION_MANAGER = "production_manager"


class Company(ModelBase):
    __tablename__ = "company"

    id: Mapped[Ints.Serial]
    bank_account_id: Mapped[Ints.Long] = mapped_column(ForeignKey("bank_account.id"))
    prefecture_id: Mapped[Ints.Long] = mapped_column(ForeignKey("prefecture.id"))
    name: Mapped[VarStrings.Char64] = mapped_column(unique=True)
    about: Mapped[VarStrings.Char256]

    prefecture = relationship("Prefecture", foreign_keys=prefecture_id)

    def __init__(self, bank_account_id: int, prefecture_id: int, name: str, about: str):
        self.bank_account_id = bank_account_id
        self.prefecture_id = prefecture_id
        self.name = name
        self.about = about


class User2Company(ModelBase):
    __tablename__ = "user_to_company"

    id: Mapped[Ints.Serial]
    user_id: Mapped[Ints.Long] = mapped_column(ForeignKey("users.id"))
    company_id: Mapped[Ints.Long] = mapped_column(ForeignKey("company.id"))
    role: Mapped[VarStrings.Char32]
    ratio: Mapped[Ints.Short]
    fired_at: Mapped[Datetime.DatetimeEmpty]  # type: ignore
    employed_at: Mapped[Datetime.Datetime]  # type: ignore

    def __init__(
        self,
        user_id: int,
        company_id: int,
        role: str,
        ratio: int,
        # fired_at: datetime.datetime | None,
        employed_at: datetime.datetime,
    ):
        self.user_id = user_id
        self.company_id = company_id
        self.role = role
        self.ratio = ratio
        # self.fired_at = fired_at
        self.employed_at = employed_at
