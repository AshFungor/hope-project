from app.env import env

import enum

import sqlalchemy
import sqlalchemy.orm

import app.modules.database.handlers as database


class Role(enum.StrEnum):
    CEO = 'CEO'
    FOUNDER = 'founder'
    EMPLOYEE = 'employee'
    CFO = 'CFO'
    MARKETING_MANAGER = 'marketing_manager'
    PRODUCTION_MANAGER = 'production_manager'


class Company(database.ModelBase):
    __tablename__ = 'company'

    id: sqlalchemy.orm.Mapped[database.serial]
    bank_account_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('bank_account.id'))
    prefecture_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('prefecture.id'))
    name: sqlalchemy.orm.Mapped[database.variable_strings[64]]
    about: sqlalchemy.orm.Mapped[database.variable_strings[256]]


class User2Company(database.ModelBase):
    __tablename__ = 'user_to_company'

    user_id: sqlalchemy.orm.Mapped[database.serial] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('bank_account.id'))
    company_id: sqlalchemy.orm.Mapped[database.serial] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('product.id'))
    role: sqlalchemy.orm.Mapped[database.variable_strings[32]]
    ratio: sqlalchemy.orm.Mapped[database.small_int]
    fired_at: sqlalchemy.orm.Mapped[database.c_datetime] = sqlalchemy.orm.mapped_column(nullable=True)
    employed_at: sqlalchemy.orm.Mapped[database.c_datetime]

    