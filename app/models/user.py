import datetime
import enum

from typing import Optional
from functools import cached_property

from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.types import Datetime, Ints, ModelBase, VarStrings


class Sex(enum.StrEnum):
    FEMALE = "female"
    MALE = "male"


class User(ModelBase, UserMixin):
    __tablename__ = "users"

    id: Mapped[Ints.Serial]
    bank_account_id: Mapped[Ints.Long] = mapped_column(ForeignKey("bank_account.id"))
    prefecture_id: Mapped[Ints.Long] = mapped_column(ForeignKey("prefecture.id"), nullable=True)
    name: Mapped[VarStrings.Char64]
    last_name: Mapped[VarStrings.Char64]
    patronymic: Mapped[VarStrings.Char64]
    login: Mapped[VarStrings.Char64]
    password: Mapped[VarStrings.Char64]
    sex: Mapped[VarStrings.Char16] = mapped_column(nullable=False)
    bonus: Mapped[Ints.Long] = mapped_column(default=0)
    birthday: Mapped[Datetime.Date]
    is_admin: Mapped[bool] = mapped_column(default=False)

    prefecture = relationship("Prefecture", foreign_keys=prefecture_id, back_populates="users")

    def __init__(
        self,
        bank_account_id: Optional[int],  # must be a valid account id
        prefecture_id: Optional[int],  # prefecture, where user belongs
        name: str,  # name of user
        last_name: str,  # last name of user
        patronymic: str,  # patronymic of user
        login: str,  # nickname for user
        password: str,  # password for login
        sex: Sex,  # some adult content
        bonus: int,  # god knows
        birthday: datetime.date,  # ...
        is_admin: bool = False,  # kek, implementing roles
    ) -> None:
        self.bank_account_id = bank_account_id
        self.prefecture_id = prefecture_id
        self.name = name
        self.last_name = last_name
        self.patronymic = patronymic
        self.login = login
        self.password = password
        self.sex = str(sex)
        self.bonus = bonus
        self.birthday = birthday
        self.is_admin = is_admin

    @cached_property
    def full_name_string(self):
        return f"{self.last_name} {self.name} {self.patronymic}"
