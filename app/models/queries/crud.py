from contextlib import contextmanager
from datetime import datetime
from enum import StrEnum
from functools import lru_cache, wraps
from random import randint
from typing import Callable, List, Set, Tuple

import sqlalchemy as orm

from app.context import AppContext, function_context
from app.models import (
    BankAccount,
    Company,
    Product,
    Product2BankAccount,
    Role,
    User,
    User2Company,
)


def wrap_crud_call(f: Callable):
    @wraps(f)
    @function_context
    def wrapper(ctx: AppContext, *args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as err:
            ctx.database.session.rollback()
            ctx.logger.error(f"CRUD failed for method {f.__name__}: {err}")

    return wrapper


@contextmanager
@function_context
def wrap_crud_context(ctx: AppContext):
    try:
        yield
    except ValueError as err:
        ctx.database.session.rollback()
        ctx.logger.error(f"CRUD failed for method: {err}")


class CRUD:
    """
    Simple CRUD methods, built to be reusable

    Take note, these methods do not commit by themselves, you have
    to call session.commit() yourself.
    """

    __ctx = AppContext.safe_load()
    # number of digits after scope id
    __bank_account_tail_len = 4

    class AccountType(StrEnum):
        CITY_HALL = "city_hall"
        COMPANY = "company"
        PREFECTURE = "prefecture"
        USER = "user"

    @classmethod
    def __from_kind(cls, kind: AccountType) -> int:
        tail = randint(10**cls.__bank_account_tail_len, 10 ** (cls.__bank_account_tail_len + 1) - 1)

        leading = 0
        match kind:
            case cls.AccountType.CITY_HALL:
                leading = cls.__ctx.config.account_mapping.city_hall
            case cls.AccountType.COMPANY:
                leading = cls.__ctx.config.account_mapping.company
            case cls.AccountType.PREFECTURE:
                leading = cls.__ctx.config.account_mapping.prefecture
            case cls.AccountType.USER:
                leading = cls.__ctx.config.account_mapping.user

        s = f"{leading}{tail}"[: 1 + cls.__bank_account_tail_len]
        return int(s)

    @classmethod
    @lru_cache
    def __existing_bank_account_ids(cls) -> Set[int]:
        return set(cls.__ctx.database.session.execute(orm.select(BankAccount.id)).all())

    @classmethod
    @wrap_crud_call
    def create_bank_account(cls, kind: AccountType) -> int:
        existing_ids = cls.__existing_bank_account_ids()

        bank_account_id = cls.__from_kind(kind)
        while bank_account_id in existing_ids:
            bank_account_id = cls.__from_kind(kind)

        bank_account = BankAccount(id=bank_account_id)
        # create money
        bind_account = Product2BankAccount(bank_account.id, cls.__ctx.config.money_product_id, 0)
        cls.__ctx.database.session.add_all([bank_account, bind_account])

        return bank_account.id

    @classmethod
    @wrap_crud_call
    def create_company(cls, company: Company):
        account = cls.create_bank_account(cls.AccountType.COMPANY)
        company.bank_account_id = account
        cls.__ctx.database.session.add(company)
        return company

    @classmethod
    @wrap_crud_call
    def create_user(cls, user: User):
        account = cls.create_bank_account(cls.AccountType.USER)
        user.bank_account_id = account
        cls.__ctx.database.session.add(user)
        return user

    @classmethod
    @wrap_crud_call
    def query_product(cls, account: int, product_id: int) -> int:
        query = cls.__ctx.database.session.scalars(
            orm.select(Product2BankAccount).filter(
                orm.and_(
                    Product2BankAccount.bank_account_id == account,
                    Product2BankAccount.product_id == product_id,
                )
            )
        ).all()

        if len(query) != 1:
            raise RuntimeError(f"internal error: query returned more than 1 or less than 1 position: {len(query)}")

        return query[0].count

    @classmethod
    @wrap_crud_call
    def query_money(cls, account: int) -> int:
        return cls.query_product(account, cls.__ctx.config.money_product_id)

    @classmethod
    @wrap_crud_call
    def query_product_by_name(cls, name: str) -> Product:
        return cls.__ctx.database.session.execute(orm.select(Product).filter(Product.name == name)).first()
