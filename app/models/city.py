import sqlalchemy
import sqlalchemy.orm

import app.modules.database.handlers as database


class City(database.ModelBase):
    __tablename__ = 'city'

    id: sqlalchemy.orm.Mapped[database.serial]
    # mayor could be null, since user depends on city, and city must be created first
    mayor_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('user.id'), nullable=True)
    prefecture_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('prefecture.id'), nullable=True)
    bank_account_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('bank_account.id'))
    name: sqlalchemy.orm.Mapped[database.variable_strings[64]]
    location: sqlalchemy.orm.Mapped[database.variable_strings[64]]


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
    prefect_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('user.id'), nullable=True)
    economic_assistant_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('user.id'), nullable=True)
    social_assistant_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('user.id'), nullable=True)


class CityHall(database.ModelBase):
    __tablename__ = 'city_hall'

    id: sqlalchemy.orm.Mapped[database.serial]
    bank_account_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('bank_account.id'))
    mayor_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('user.id'))
    economic_assistant_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('user.id'))
    social_assistant_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('user.id'))


class Infrastructure(database.ModelBase):
    __tablename__ = 'infrastructure'

    id: sqlalchemy.orm.Mapped[database.serial]
    prefecture_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('prefecture.id'))
    name: sqlalchemy.orm.Mapped[database.variable_strings[64]]
