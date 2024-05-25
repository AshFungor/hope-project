import enum
import datetime

import sqlalchemy
import sqlalchemy.orm

import app.modules.database.handlers as database
import app.modules.database.validators as validators

import dateutil


class Sex(enum.StrEnum):
    FEMALE = 'female'
    MALE = 'male'
    OTHER = 'other'


class User(database.ModelBase):
    __tablename__ = 'users'

    id: sqlalchemy.orm.Mapped[database.serial]
    bank_account_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('bank_account.id'))
    city_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('city.id'), nullable=True) 
    name: sqlalchemy.orm.Mapped[database.variable_strings[64]]
    last_name: sqlalchemy.orm.Mapped[database.variable_strings[64]]
    login: sqlalchemy.orm.Mapped[database.variable_strings[64]]
    password: sqlalchemy.orm.Mapped[database.variable_strings[64]]
    sex: sqlalchemy.orm.Mapped[database.variable_strings[16]] = sqlalchemy.orm.mapped_column(nullable=False)
    bonus: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(default=0)
    birthday: sqlalchemy.orm.Mapped[database.c_date]


    def __init__(
        self,
        bank_account_id : int | None,   # must be a valid account id
        city_id : int,                  # city, where user belongs
        name: str,                      # name of user
        last_name: str,                 # last name of user
        login: str,                     # nickname for user
        password: str,                  # password for login
        sex: Sex,                       # some adult content
        bonus: int,                     # god knows
        birthday: datetime.date         # ...
    ) -> None:
        # TODO: generate bank account in case none
        self.bank_account_id = bank_account_id
        self.city_id = city_id
        self.name = validators.PureRussianTextValidator.validate(name, 64)
        self.last_name = validators.PureRussianTextValidator.validate(last_name, 64)
        self.login = validators.NoWhitespaceGenericTextValidator.validate(login, 64)
        self.password = validators.NoWhitespaceGenericTextValidator.validate(password, 64)
        self.sex = validators.EnumValidator.validate(str(sex), Sex, str(Sex.OTHER))
        self.bonus = validators.IntValidator.validate(bonus, 64, True)
        self.birthday = validators.DtValidator.validate(birthday)

    def __repr__(self) -> str:
        return '<User object with fields: ' + ';'.join([f'field: <{attr}> with value: {repr(value)}' for attr, value in self.__dict__]) + '>'


class Goal(database.ModelBase):
    __tablename__ = 'goal'

    id: sqlalchemy.orm.Mapped[database.serial]
    bank_account_id: sqlalchemy.orm.Mapped[database.long_int] = sqlalchemy.orm.mapped_column(sqlalchemy.ForeignKey('bank_account.id'))
    created_at: sqlalchemy.orm.Mapped[database.c_datetime]
    rate: sqlalchemy.orm.Mapped[database.small_int]
    complete: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False)

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
