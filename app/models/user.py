import datetime
import enum

from flask_login import UserMixin
from sqlalchemy import ForeignKey
from functools import cached_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.database import Datetime, Ints, ModelBase, VarStrings


class Sex(enum.StrEnum):
    FEMALE = "female"
    MALE = "male"


class User(ModelBase, UserMixin):
    __tablename__ = "users"

    id: Mapped[Ints.Serial]
    bank_account_id: Mapped[Ints.Long] = mapped_column(ForeignKey("bank_account.id"))
    city_id: Mapped[Ints.Int] = mapped_column(ForeignKey("city.id"), nullable=True)
    name: Mapped[VarStrings.Char64]
    last_name: Mapped[VarStrings.Char64]
    patronymic: Mapped[VarStrings.Char64]
    login: Mapped[VarStrings.Char64]
    password: Mapped[VarStrings.Char64]
    sex: Mapped[VarStrings.Char16] = mapped_column(nullable=False)
    bonus: Mapped[Ints.Long] = mapped_column(default=0)
    birthday: Mapped[Datetime.Date]
    is_admin: Mapped[bool] = mapped_column(default=False)

    city = relationship("City", foreign_keys=city_id, back_populates="users")

    def __init__(
        self,
        bank_account_id: int | None,  # must be a valid account id
        city_id: int,  # city, where user belongs
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
        # TODO: generate bank account in case none
        self.bank_account_id = bank_account_id
        self.city_id = city_id
        self.name = name
        self.last_name = last_name
        self.patronymic = patronymic.strip()
        self.login = login
        self.password = password
        self.sex = str(sex)
        self.bonus = bonus
        self.birthday = birthday
        self.is_admin = is_admin

    @cached_property
    def full_name_string(self):
        return f'{self.last_name} {self.name} {self.patronymic}'


class Goal(ModelBase):
    __tablename__ = "goal"

    id: Mapped[Ints.Serial]
    bank_account_id: Mapped[Ints.Long] = mapped_column(ForeignKey("bank_account.id"))
    created_at: Mapped[Datetime.Datetime]
    amount_on_setup: Mapped[Ints.Long] = mapped_column(nullable=False)
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

    # def get_rate(self, current: int) -> float:
    #     distance = max(self.value - current + self.amount_on_setup, 0)
    #     if distance:
    #         return max(round((1 - distance / self.value) * 100, 2), 0)
    #     return 100

    # @staticmethod
    # def get_last(bank_account: int, limitByCurrentDay: bool = False) -> typing.Union["Goal", None]:
    #     last = (
    #         env.db.impl().session.execute(orm.select(Goal).filter_by(bank_account_id=bank_account).order_by(Goal.created_at.desc())).scalars().first()
    #     )
    #     if not last or limitByCurrentDay and last.created_at.date() < datetime.datetime.now().date():
    #         return None
    #     return last
