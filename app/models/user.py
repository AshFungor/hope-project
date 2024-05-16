import enum

import sqlalchemy
import sqlalchemy.orm

import app.modules.database.handlers as database


class Sex(enum.StrEnum):
    FEMALE = 'female'
    MALE = 'male'


class User(database.ModelBase):
    __tablename__ = 'user'

    id: sqlalchemy.orm.Mapped[database.serial]
    bank_account_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('bank_account.id'))
    city_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('city.id')) 
    name: sqlalchemy.orm.Mapped[database.variable_strings[64]]
    last_name: sqlalchemy.orm.Mapped[database.variable_strings[64]]
    login: sqlalchemy.orm.Mapped[database.variable_strings[64]]
    password: sqlalchemy.orm.Mapped[database.variable_strings[64]]
    sex: sqlalchemy.orm.Mapped[database.variable_strings[16]] = sqlalchemy.orm.mapped_column(nullable=False)
    bonus: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(default=0)
    birthday: sqlalchemy.orm.Mapped[database.c_date]


class Goal(database.ModelBase):
    __tablename__ = 'goal'

    id: sqlalchemy.orm.Mapped[database.serial]
    bank_account_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('bank_account.id'))
    created_at: sqlalchemy.orm.Mapped[database.c_datetime]
    rate: sqlalchemy.orm.Mapped[database.small_int]
    complete: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False)


