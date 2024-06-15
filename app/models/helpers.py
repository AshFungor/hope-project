import datetime

from sqlalchemy import select

from app.env import env

from .bank_account import Product2BankAccount
from .user import Goal


def get_last_goal_by_bank_account(banc_account_id: int) -> Goal | None:
    return (
        env.db.impl()
        .session.execute(
            select(Goal)
            .filter_by(bank_account_id=banc_account_id)
            .order_by(Goal.created_at.desc())
        )
        .scalars()
        .first()
    )


def get_goal_on_current_day(banc_account_id: int) -> Goal | None:
    goal = get_last_goal_by_bank_account(banc_account_id)
    return None if not goal or goal.created_at.date() != datetime.date.today() else goal


def get_bank_account_size(banc_account_id: int) -> int | None:
    return (
        env.db.impl()
        .session.execute(
            select(Product2BankAccount.count).filter_by(
                bank_account_id=banc_account_id, product_id=1
            )
        )
        .scalars()
        .first()
    )
