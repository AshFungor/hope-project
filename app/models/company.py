from app.env import env

import enum
import datetime

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import ForeignKey

from app.modules.database.handlers import serial
from app.modules.database.handlers import long_int
from app.modules.database.handlers import c_datetime
from app.modules.database.handlers import variable_strings
from app.modules.database.handlers import small_int
from app.modules.database.handlers import ModelBase

import app.modules.database.validators as validators


class Role(enum.StrEnum):
    CEO = 'CEO'
    FOUNDER = 'founder'
    EMPLOYEE = 'employee'
    CFO = 'CFO'
    MARKETING_MANAGER = 'marketing_manager'
    PRODUCTION_MANAGER = 'production_manager'


class Company(ModelBase):
    __tablename__ = 'company'

    id: Mapped[serial]
    bank_account_id: Mapped[long_int] = mapped_column(ForeignKey('bank_account.id'))
    prefecture_id: Mapped[long_int] = mapped_column(ForeignKey('prefecture.id'))
    name: Mapped[variable_strings[64]] = mapped_column(unique=True)
    about: Mapped[variable_strings[256]]

    def __init__(
        self, 
        bank_account_id: int,
        prefecture_id: int,
        name: str,
        about: str
    ) -> None:
        self.bank_account_id = validators.IntValidator.validate(bank_account_id, 64, False)
        self.prefecture_id = validators.IntValidator.validate(prefecture_id, 64, False)
        self.name = validators.GenericTextValidator(name, 64, False)
        self.about = validators.GenericTextValidator(about, 256, False)

    def __repr__(self) -> str:
        return '<Company object with fields: ' + ';'.join([f'field: <{attr}> with value: {repr(value)}' for attr, value in self.__dict__.items()]) + '>'


class User2Company(ModelBase):
    __tablename__ = 'user_to_company'

    id: Mapped[serial]
    user_id: Mapped[long_int] = mapped_column(ForeignKey('users.id'))
    company_id: Mapped[long_int] = mapped_column(ForeignKey('company.id'))
    role: Mapped[variable_strings[32]]
    ratio: Mapped[small_int]
    fired_at: Mapped[c_datetime] = mapped_column(default=None, nullable=True)
    employed_at: Mapped[c_datetime]

    def __init__(
        self,
        user_id: int,
        company_id: int,
        role: str,
        ratio: int,
        fired_at: datetime.datetime,
        employed_at: datetime.datetime
    ) -> None:
        self.user_id = validators.IntValidator.validate(user_id, 64, False)
        self.company_id = validators.IntValidator.validate(company_id, 64, False)
        self.role = validators.GenericTextValidator.validate(role, 32, False)
        self.ratio = validators.IntValidator.validate(ratio, 16, True)
        self.fired_at = validators.DtValidator.validate(fired_at)
        self.employed_at = validators.DtValidator.validate(employed_at)

    def __repr__(self) -> str:
        return '<User2Company object with fields: ' + ';'.join([f'field: <{attr}> with value: {repr(value)}' for attr, value in self.__dict__.items()]) + '>'
