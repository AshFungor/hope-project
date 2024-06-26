import sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.modules.database.handlers import serial
from app.modules.database.handlers import long_int
from app.modules.database.handlers import variable_strings
from app.modules.database.handlers import c_datetime
from app.modules.database.handlers import ModelBase
from app.modules.database.handlers import c_datetime_fired

import app.modules.database.validators as validators
import app.models as models
from app.env import env


class City(ModelBase):
    __tablename__ = 'city'

    id: Mapped[serial]
    # mayor could be null, since user depends on city, and city must be created first
    mayor_id: Mapped[long_int] = mapped_column(ForeignKey('users.id'), nullable=True)
    prefecture_id: Mapped[long_int] = mapped_column(
        ForeignKey('prefecture.id'), nullable=True
    )
    bank_account_id: Mapped[long_int] = mapped_column(ForeignKey('bank_account.id'))
    name: Mapped[variable_strings[64]]
    location: Mapped[variable_strings[64]]

    mayor = relationship('User', foreign_keys=mayor_id)
    prefecture = relationship('Prefecture', back_populates='cities')
    users = relationship('User', foreign_keys='User.city_id', back_populates='city')

    def __init__(
        self,
        name: str,
        mayor_id: int | None,
        prefecture_id: int | None,
        bank_account_id: int | None,
        location: str,
    ) -> None:
        self.mayor_id = mayor_id
        self.prefecture_id = prefecture_id
        self.bank_account_id = bank_account_id
        self.name = validators.GenericTextValidator.validate(name, 64)
        self.location = validators.GenericTextValidator.validate(location, 64)

    @staticmethod
    def get_all() -> list[str]:
        return [city.name for city in env.db.impl().session.execute(
            sqlalchemy.select(models.City)
        ).scalars().all()]


class Office(ModelBase):
    __tablename__ = 'office'

    id: Mapped[serial]
    city_id: Mapped[long_int] = mapped_column(ForeignKey('city.id'))
    company_id: Mapped[long_int] = mapped_column(ForeignKey('company.id'))
    founded_at: Mapped[c_datetime]
    dismissed_at: Mapped[c_datetime_fired]

    city = relationship('City', foreign_keys=city_id)
    company = relationship('Company', foreign_keys=company_id)


class Prefecture(ModelBase):
    __tablename__ = 'prefecture'

    id: Mapped[serial]
    name: Mapped[variable_strings[64]] = mapped_column(nullable=True)
    bank_account_id: Mapped[long_int] = mapped_column(ForeignKey('bank_account.id'))
    prefect_id: Mapped[long_int] = mapped_column(ForeignKey('users.id'), nullable=True)
    economic_assistant_id: Mapped[long_int] = mapped_column(
        ForeignKey('users.id'), nullable=True
    )
    social_assistant_id: Mapped[long_int] = mapped_column(
        ForeignKey('users.id'), nullable=True
    )

    prefect = relationship('User', foreign_keys=prefect_id)
    economic_assistant = relationship('User', foreign_keys=economic_assistant_id)
    social_assistant = relationship('User', foreign_keys=social_assistant_id)
    cities = relationship('City', back_populates='prefecture')
    infrastructures = relationship('Infrastructure')

    def __init__(
        self,
        name: str,
        bank_account_id: int | None,
        prefect_id: int | None,
        economic_assistant_id: int | None,
        social_assistant_id: int | None,
    ) -> None:
        self.bank_account_id = bank_account_id
        self.prefect_id = prefect_id
        self.economic_assistant_id = economic_assistant_id
        self.social_assistant_id = social_assistant_id
        self.name = validators.GenericTextValidator.validate(name, 64)

    def __repr__(self) -> str:
        return (
            '<Prefecture object with fields: '
            + ';'.join(
                [
                    f'field: <{attr}> with value: {repr(value)}'
                    for attr, value in self.__dict__.items()
                ]
            )
            + '>'
        )


class CityHall(ModelBase):
    __tablename__ = 'city_hall'

    id: Mapped[serial]
    bank_account_id: Mapped[long_int] = mapped_column(ForeignKey('bank_account.id'))
    mayor_id: Mapped[long_int] = mapped_column(ForeignKey('users.id'))
    economic_assistant_id: Mapped[long_int] = mapped_column(ForeignKey('users.id'))
    social_assistant_id: Mapped[long_int] = mapped_column(ForeignKey('users.id'))


class Infrastructure(ModelBase):
    __tablename__ = 'infrastructure'

    id: Mapped[serial]
    prefecture_id: Mapped[long_int] = mapped_column(ForeignKey('prefecture.id'))
    name: Mapped[variable_strings[64]]
