import sqlalchemy

from app import models
from app.env import env

import enum
import datetime

from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column
from sqlalchemy import ForeignKey

from app.modules.database.handlers import serial
from app.modules.database.handlers import long_int
from app.modules.database.handlers import c_datetime, c_datetime_fired
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

    prefecture = relationship('Prefecture', foreign_keys=prefecture_id)
    offices = relationship('Office', back_populates='company')

    def __init__(
        self,
        bank_account_id: int,
        prefecture_id: int,
        name: str,
        about: str
    ) -> None:
        self.bank_account_id = validators.IntValidator.validate(bank_account_id, 64, False)
        self.prefecture_id = validators.IntValidator.validate(prefecture_id, 64, False)
        self.name = validators.GenericTextValidator.validate(name, 64, False)
        self.about = validators.GenericTextValidator.validate(about, 256, False)

    def __repr__(self) -> str:
        return '<Company object with fields: ' + ';'.join([f'field: <{attr}> with value: {repr(value)}' for attr, value in self.__dict__.items()]) + '>'

    @staticmethod
    def id_to_company(id: str):
        company = env.db.impl().session.execute(
            sqlalchemy.select(
                models.Company
            ).filter(
                models.Company.id == id
            )
        ).scalars().first()
        return company


class User2Company(ModelBase):
    __tablename__ = 'user_to_company'

    id: Mapped[serial]
    user_id: Mapped[long_int] = mapped_column(ForeignKey('users.id'))
    company_id: Mapped[long_int] = mapped_column(ForeignKey('company.id'))
    role: Mapped[variable_strings[32]]
    ratio: Mapped[small_int]
    fired_at: Mapped[c_datetime_fired]
    employed_at: Mapped[c_datetime]

    def __init__(
        self,
        user_id: int,
        company_id: int,
        role: str,
        ratio: int,
        # fired_at: datetime.datetime | None,
        employed_at: datetime.datetime
    ) -> None:
        self.user_id = validators.IntValidator.validate(user_id, 64, False)
        self.company_id = validators.IntValidator.validate(company_id, 64, False)
        self.role = validators.GenericTextValidator.validate(role, 32, False)
        self.ratio = validators.IntValidator.validate(ratio, 16, True)
        # self.fired_at = fired_at
        self.employed_at = validators.DtValidator.validate(employed_at)

    def __repr__(self) -> str:
        return '<User2Company object with fields: ' + ';'.join([f'field: <{attr}> with value: {repr(value)}' for attr, value in self.__dict__.items()]) + '>'


'''Условия приема на должность:
1) В компании не должно быть двух работников на одно и той же должности (кроме рабочих).
2) Один пользователь может занимать только одну должность в одной компании.
3) Найм должен осуществляться только ген. директором компании или ее основателем
'''


class CompanyAction(enum.Enum):
    FOUNDER_HIRES = "founder  hires"
    CEO_HIRES = "CEO hiring"
    PRODUCT_MANAGER_HIRES = "product manager hires"
    WORKING_WITH_EMPLOYEES = 'working with employees'
    HIRING = 'hiring'
    ...


class CompanyActionPolicy:

    def check_rights(
            self,
            user_id: str,
            company_id: str,
            action: CompanyAction,
            hire_role: str = None
    ) -> bool:
        user_role = self.get_user_role(company_id=company_id, user_id=user_id)
        if action == CompanyAction.HIRING:
            hiring_mapper = {
                'CEO': CompanyAction.FOUNDER_HIRES,
                'CFO': CompanyAction.CEO_HIRES,
                'marketing_manager': CompanyAction.CEO_HIRES,
                'production_manager': CompanyAction.CEO_HIRES,
                'employee': CompanyAction.PRODUCT_MANAGER_HIRES,
            }
            action = hiring_mapper.get(hire_role)
        if not (action is None):
            available_action = {
                CompanyAction.FOUNDER_HIRES: (
                    Role.FOUNDER.value,
                ),
                CompanyAction.CEO_HIRES: (
                    Role.CEO.value
                ),
                CompanyAction.PRODUCT_MANAGER_HIRES: (
                    Role.PRODUCTION_MANAGER.value
                ),
                CompanyAction.WORKING_WITH_EMPLOYEES: (
                    Role.FOUNDER.value,
                    Role.CEO.value,
                    Role.PRODUCTION_MANAGER.value
                )
            }
            return user_role in available_action[action]
        return False

    def get_user_role(self, user_id: str, company_id: str) -> Role:
        user_role_query = (
            sqlalchemy.select(
                User2Company.role
            )
            .filter(
                sqlalchemy.and_(
                    User2Company.user_id == user_id,
                    User2Company.company_id == company_id
                )
            )
        )
        user_role = env.db.impl().session.execute(user_role_query).scalars().first()
        return user_role


companyActionPolicy = CompanyActionPolicy()
