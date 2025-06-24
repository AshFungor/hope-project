import sqlalchemy as orm

from typing import Callable, List, Tuple
from datetime import datetime
from functools import wraps

from app.context import context, AppContext
from app.models import BankAccount, Product2BankAccount, Company, User2Company, Role


@context
def wrap_crud_call(ctx: AppContext, f: Callable):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as err:
            ctx.database.session.rollback()
            ctx.logger.error(f'CRUD failed for method {f.__name__}: {err}')

    return wrapper


class CRUD:
    __ctx = AppContext.safe_load()

    @classmethod
    @wrap_crud_call
    def create_bank_account(cls) -> int:
        bank_account = BankAccount.from_kind(BankAccount.AccountMapping.COMPANY)
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
    def read_money(cls, id: int) -> int:
        query = cls.__ctx.database.session.scalars(
            orm
            .select(Product2BankAccount)
            .filter(
                orm.and_(
                    Product2BankAccount.bank_account_id == id,
                    Product2BankAccount.product_id == 1,
                )
            )
        ).all()

        if len(query) != 1:
            return f"internal error: query returned more than 1 or less than 1 position: {len(query)}"

        return query[0].count
