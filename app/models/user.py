import enum
import math
import typing
import logging
import dateutil
import datetime

import flask_login

from app.env import env
from functools import cached_property

import sqlalchemy as orm

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import ForeignKey

from app.modules.database.handlers import serial
from app.modules.database.handlers import c_date
from app.modules.database.handlers import long_int
from app.modules.database.handlers import small_int
from app.modules.database.handlers import c_datetime
from app.modules.database.handlers import variable_strings
from app.modules.database.handlers import ModelBase

import app.modules.database.validators as validators



class Sex(enum.StrEnum):
    FEMALE = 'female'
    MALE = 'male'


class User(ModelBase, flask_login.UserMixin):
    __tablename__ = 'users'

    id: Mapped[serial]
    bank_account_id: Mapped[long_int] = mapped_column(ForeignKey('bank_account.id'))
    city_id: Mapped[long_int] = mapped_column(ForeignKey('city.id'), nullable=True)
    name: Mapped[variable_strings[64]]
    last_name: Mapped[variable_strings[64]]
    patronymic: Mapped[variable_strings[64]]
    login: Mapped[variable_strings[64]]
    password: Mapped[variable_strings[64]]
    sex: Mapped[variable_strings[16]] = mapped_column(nullable=False)
    bonus: Mapped[long_int] = mapped_column(default=0)
    birthday: Mapped[c_date]
    is_admin: Mapped[bool] = mapped_column(default=False)

    city = relationship('City', foreign_keys=city_id, back_populates='users')


    def __init__(
        self,
        bank_account_id : int | None,   # must be a valid account id
        city_id : int,                  # city, where user belongs
        name: str,                      # name of user
        last_name: str,                 # last name of user
        patronymic: str,                # patronymic of user
        login: str,                     # nickname for user
        password: str,                  # password for login
        sex: Sex,                       # some adult content
        bonus: int,                     # god knows
        birthday: datetime.date,        # ...
        is_admin: bool = False          # kek, implementing roles
    ) -> None:
        # TODO: generate bank account in case none
        self.bank_account_id = bank_account_id
        self.city_id = city_id
        self.name = validators.PureRussianTextValidator.validate(name, 64)
        self.last_name = validators.PureRussianTextValidator.validate(last_name, 64)
        self.patronymic = patronymic.strip()
        self.login = validators.NoWhitespaceGenericTextValidator.validate(login, 64)
        self.password = validators.NoWhitespaceGenericTextValidator.validate(password, 64)
        self.sex = validators.EnumValidator.validate(str(sex), Sex, str(Sex.MALE))
        self.bonus = validators.IntValidator.validate(bonus, 64, True)
        self.birthday = validators.DtValidator.validate(birthday)
        self.is_admin = is_admin


    def __repr__(self) -> str:
        return '<User object with fields: ' + ';'.join([f'field: <{attr}> with value: {repr(value)}' for attr, value in self.__dict__.items()]) + '>'

    @cached_property
    def full_name_string(self):
        return f"{self.last_name} {self.name} {self.patronymic}"


class Goal(ModelBase):
    __tablename__ = 'goal'

    id: Mapped[serial]
    bank_account_id: Mapped[long_int] = mapped_column(ForeignKey('bank_account.id'))
    created_at: Mapped[c_datetime]
    amount_on_setup: Mapped[long_int] = mapped_column(nullable=False)
    value: Mapped[long_int] = mapped_column(nullable=False)
    amount_on_validate: Mapped[long_int] = mapped_column(nullable=True)
    complete: Mapped[bool] = mapped_column(default=False)

    def __init__(
        self,
        bank_account_id: int,
        value: int,
        amount_on_setup: int,
        amount_on_validate: int | None = None,
        created_at: datetime.datetime | None = datetime.datetime.now(validators.CurrentTimezone),
        complete: bool | None = False
    ) -> None:
        self.bank_account_id = bank_account_id
        self.value = value
        self.amount_on_setup = amount_on_setup
        self.amount_on_validate = amount_on_validate
        self.created_at = validators.DtValidator.validate(
            created_at, 
            lower=datetime.datetime.now(validators.CurrentTimezone) - dateutil.relativedelta.relativedelta(days=1)
        )
        self.complete = complete

    def __repr__(self) -> str:
        return '<Goal object with fields: ' + ';'.join([f'field: <{attr}> with value: {repr(value)}' for attr, value in self.__dict__.items()]) + '>'

    @cached_property
    def local_created_at(self):
        return self.created_at.astimezone(tz=validators.CurrentTimezone)
    
    def get_rate(self, current: int) -> float:
        distance = max(self.value - current + self.amount_on_setup, 0)
        if distance:
            return max(round((1 - distance / self.value) * 100, 2), 0)
        return 100

    @staticmethod
    def get_last(bank_account: int, limitByCurrentDay: bool = False) -> typing.Union['Goal', None]:
        last = env.db.impl().session.execute(
                orm.select(Goal)
                .filter_by(bank_account_id=bank_account)
                .order_by(Goal.created_at.desc())
            )               \
            .scalars()      \
            .first()
        if not last or limitByCurrentDay and \
            last.local_created_at.date() != datetime.datetime.now(tz=validators.CurrentTimezone).date():
            return None
        return last

