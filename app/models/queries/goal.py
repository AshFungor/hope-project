from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import sqlalchemy as orm

from app.context import AppContext, function_context
from app.models import BankAccount, Goal, Transaction, TransactionStatus
from app.models.queries import CRUD


@function_context
def get_last(ctx: AppContext, bank_account: int, current_day_only: bool = False) -> Optional[Goal]:
    last = ctx.database.session.scalar(orm.select(Goal).filter(Goal.bank_account_id == bank_account).order_by(Goal.created_at.desc()))

    if not last:
        return None

    if current_day_only and last.created_at.date() < datetime.now().date():
        return None

    return last


# class GoalProgress:
#     @dataclass
#     class GoalProgressProperties:
#         goal: Goal
#         bank_account_id: int
#         span: timedelta

#     @classmethod
#     def calculate_progress_for_prefecture(ctx: AppContext, properties: GoalProgressProperties) -> Optional[int]:
#         ctx.database.session.


@function_context
def calculate_progress(ctx: AppContext, bank_account_id: int, goal: Goal, span: timedelta) -> Optional[int]:
    bank_account = ctx.database.session.get(BankAccount, bank_account_id)
    if bank_account is None:
        return None

    if not goal:
        return None

    money = CRUD.query_money(bank_account_id)

    to_lift = (
        ctx.database.session.scalar(
            orm.select(orm.func.sum(Transaction.count)).filter(
                orm.or_(
                    orm.cast(Transaction.customer_bank_account_id, orm.String).startswith(str(ctx.config.account_mapping.prefecture)),
                    orm.cast(Transaction.customer_bank_account_id, orm.String).startswith(str(ctx.config.account_mapping.city_hall)),
                ),
                Transaction.status == TransactionStatus.ACCEPTED,
                Transaction.product_id == ctx.config.money_product_id,
                Transaction.created_at >= datetime.now() - span,
                Transaction.seller_bank_account_id == bank_account_id,
            )
        )
        or 0
    )

    return int(money - goal.amount_on_setup + to_lift)
