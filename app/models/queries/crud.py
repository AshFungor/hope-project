from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from typing import Callable, List, Tuple

import sqlalchemy as orm

from app.context import AppContext, function_context
from app.models import BankAccount, Company, Product2BankAccount, Role, User2Company, User, Product


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
    """Simple CRUD methods, built to be reusable"""

    __ctx = AppContext.safe_load()

    @classmethod
    @wrap_crud_call
    def create_bank_account(cls, kind: BankAccount.AccountMapping) -> int:
        bank_account = BankAccount.from_kind(kind)
        bind_account = Product2BankAccount(bank_account.id, 1, 0)
        cls.__ctx.database.session.add_all(bank_account, bind_account)
        return bank_account.id

    @classmethod
    @wrap_crud_call
    def create_company(cls, company: Company, founders: List[Tuple[int, float]]):
        cls.__ctx.database.session.add(company)
        cls.__ctx.database.session.add_all(
            [User2Company(founder_id, company.id, Role.FOUNDER, ratio, datetime.now()) for founder_id, ratio in founders]
        )

        cls.__ctx.database.session.commit()

    @classmethod
    @wrap_crud_call
    def create_user(cls, user: User):
        account = cls.create_bank_account(BankAccount.AccountMapping.USER)
        user.bank_account_id = account
        cls.__ctx.database.session.add(user)

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
        return cls.query_product(account, 1)
    
    @classmethod
    @wrap_crud_call
    def query_product_by_name(cls, name: str) -> Product:
        return cls.__ctx.database.session.execute(
            orm.select(Product).filter(Product.name == name)
        ).first()
