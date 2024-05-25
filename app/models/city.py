import sqlalchemy
import sqlalchemy.orm

import app.modules.database.handlers as database
import app.modules.database.validators as validators


class City(database.ModelBase):
    __tablename__ = 'city'

    id: sqlalchemy.orm.Mapped[database.serial]
    # mayor could be null, since user depends on city, and city must be created first
    mayor_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('users.id'), nullable=True)
    prefecture_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('prefecture.id'), nullable=True)
    bank_account_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('bank_account.id'))
    name: sqlalchemy.orm.Mapped[database.variable_strings[64]]
    location: sqlalchemy.orm.Mapped[database.variable_strings[64]]

    def __init__(
        self,
        name: str,
        mayor_id: int | None,
        prefecture_id: int | None,
        bank_account_id: int | None,
        location: str
    ) -> None:
        self.mayor_id = mayor_id
        self.prefecture_id = prefecture_id
        self.bank_account_id = bank_account_id
        self.name = validators.GenericTextValidator.validate(name, 64)
        self.location = validators.GenericTextValidator.validate(location, 64)


class Office(database.ModelBase):
    __tablename__ = 'office'

    id: sqlalchemy.orm.Mapped[database.serial]
    city_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('city.id'))
    company_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('product.id'))
    founded_at: sqlalchemy.orm.Mapped[database.c_datetime]
    dismissed_at: sqlalchemy.orm.Mapped[database.c_datetime] = sqlalchemy.orm.mapped_column(nullable=True)


class Prefecture(database.ModelBase):
    __tablename__ = 'prefecture'

    id: sqlalchemy.orm.Mapped[database.serial]
    name: sqlalchemy.orm.Mapped[database.variable_strings[64]] = sqlalchemy.orm.mapped_column(nullable=True)
    bank_account_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('bank_account.id'))
    prefect_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('users.id'), nullable=True)
    economic_assistant_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('users.id'), nullable=True)
    social_assistant_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('users.id'), nullable=True)

    def __init__(
        self,
        name: str,
        bank_account_id: int | None,
        prefect_id: int | None,
        economic_assistant_id: int | None,
        social_assistant_id: int | None
    ) -> None:
        self.bank_account_id = bank_account_id
        self.prefect_id = prefect_id
        self.economic_assistant_id = economic_assistant_id
        self.social_assistant_id = social_assistant_id
        self.name = validators.GenericTextValidator.validate(name, 64)
    
    def __repr__(self) -> str:
        return '<Prefecture object with fields: ' + ';'.join([f'field: <{attr}> with value: {repr(value)}' for attr, value in self.__dict__]) + '>'

class CityHall(database.ModelBase):
    __tablename__ = 'city_hall'

    id: sqlalchemy.orm.Mapped[database.serial]
    bank_account_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('bank_account.id'))
    mayor_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('users.id'))
    economic_assistant_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('users.id'))
    social_assistant_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('users.id'))


class Infrastructure(database.ModelBase):
    __tablename__ = 'infrastructure'

    id: sqlalchemy.orm.Mapped[database.serial]
    prefecture_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('prefecture.id'))
    name: sqlalchemy.orm.Mapped[database.variable_strings[64]]
