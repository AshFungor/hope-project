import sqlalchemy as orm

from typing import Optional
from datetime import datetime

from app.models import Goal
from app.context import function_context, AppContext


@function_context
def get_last(ctx: AppContext, bank_account: int, current_day_only: bool = False) -> Optional[Goal]:
    last = ctx.database.session.scalar(
        orm
        .select(Goal)
        .filter(Goal.bank_account_id == bank_account)
        .order_by(Goal.created_at.desc())
    )

    if not last:
        return None

    if current_day_only and last.created_at.date() < datetime.now().date():
        return None

    return last
