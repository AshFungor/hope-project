from datetime import datetime
from typing import Optional

import sqlalchemy as orm

from app.context import AppContext, class_context
from app.models import Product, Sex, User
from app.models.queries import CRUD


class TestCRUD:
    """CRUD wrappers for yielding test orm objects"""

    __ctx = AppContext.safe_load()

    @classmethod
    def create_user(
        cls,
        prefecture_id: Optional[int] = None,
        name: str = "some_user",
        last_name: str = "some_last_name",
        patronymic: str = "some_last_last_name",
        login: str = "some_login",
        password: str = "some_password",
        sex: Sex = Sex.MALE,
        bonus: int = 0,
        birthday: Optional[datetime] = None,
        is_admin: bool = False,
    ) -> User:
        birthday = datetime.now() if birthday is None else birthday
        user = CRUD.create_user(
            User(
                bank_account_id=None,
                prefecture_id=prefecture_id,
                name=name,
                last_name=last_name,
                patronymic=patronymic,
                login=login,
                password=password,
                sex=sex,
                bonus=bonus,
                birthday=birthday,
                is_admin=is_admin,
            )
        )

        cls.__ctx.database.session.commit()
        return user

    @classmethod
    @class_context
    def create_money(cls, ctx: AppContext):
        ctx.database.session.add(Product(id=ctx.config.money_product_id, name="money", category="MONEY", level=0))
        cls.__ctx.database.session.commit()
