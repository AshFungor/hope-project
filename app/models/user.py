import enum
import datetime

from flask_login import UserMixin

from app.env import env

from sqlalchemy import ForeignKey
from  sqlalchemy.orm import Mapped, mapped_column

from app.modules.database.handlers import long_int, ModelBase, serial, variable_strings, c_date, small_int, c_datetime
import app.modules.database.validators as validators

import dateutil


class Sex(enum.StrEnum):
    FEMALE = 'female'
    MALE = 'male'


class User(ModelBase, UserMixin):
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
        birthday: datetime.date,         # ...
        is_admin: bool = False
    ) -> None:
        # TODO: generate bank account in case none
        self.bank_account_id = bank_account_id
        self.city_id = city_id
        self.name = validators.PureRussianTextValidator.validate(name, 64)
        self.last_name = validators.PureRussianTextValidator.validate(last_name, 64)
        self.patronymic = validators.PureRussianTextValidator.validate(patronymic, 64)
        self.login = validators.NoWhitespaceGenericTextValidator.validate(login, 64)
        self.password = validators.NoWhitespaceGenericTextValidator.validate(password, 64)
        self.sex = validators.EnumValidator.validate(str(sex), Sex, str(Sex.MALE))
        self.bonus = validators.IntValidator.validate(bonus, 64, True)
        self.birthday = validators.DtValidator.validate(birthday)
        self.is_admin = is_admin


    def __repr__(self) -> str:
        return '<User object with fields: ' + ';'.join([f'field: <{attr}> with value: {repr(value)}' for attr, value in self.__dict__.items()]) + '>'


class Goal(ModelBase):
    __tablename__ = 'goal'

    id: Mapped[serial]
    bank_account_id: Mapped[long_int] = mapped_column(ForeignKey('bank_account.id'))
    created_at: Mapped[c_datetime]
    rate: Mapped[small_int]
    complete: Mapped[bool] = mapped_column(default=False)

    def __init__(
        self,
        bank_account_id : int,
        rate: int,
        created_at: datetime.datetime | None = datetime.datetime.now(validators.CurrentTimezone),
        complete: bool | None = False
    ) -> None:
        self.bank_account_id = bank_account_id
        self.rate = validators.IntValidator.validate(rate, 16, True)
        self.created_at = validators.DtValidator.validate(
            created_at, 
            lower=datetime.datetime.now(validators.CurrentTimezone) - dateutil.relativedelta.relativedelta(days=1)
        )
        self.complete = complete

    def __repr__(self) -> str:
        return '<Goal object with fields: ' + ';'.join([f'field: <{attr}> with value: {repr(value)}' for attr, value in self.__dict__]) + '>'
