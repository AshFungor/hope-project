from app.env import env

import sqlalchemy
import sqlalchemy.orm

import app.modules.database.handlers


class User(app.modules.database.handlers.ModelBase):
    __tablename__ = 'user'

    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(sqlalchemy.String(50))
