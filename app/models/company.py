from app.env import env

import enum

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from app.modules.database.handlers import ModelBase, serial, long_int, variable_strings, small_int, c_datetime


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
    name: Mapped[variable_strings[64]]
    about: Mapped[variable_strings[256]]


class User2Company(ModelBase):
    __tablename__ = 'user_to_company'

    user_id: Mapped[serial] = mapped_column(ForeignKey('bank_account.id'))
    company_id: Mapped[serial] = mapped_column(ForeignKey('product.id'))
    role: Mapped[variable_strings[32]]
    ratio: Mapped[small_int]
    fired_at: Mapped[c_datetime] = mapped_column(nullable=True)
    employed_at: Mapped[c_datetime]
