from datetime import datetime, timedelta

import sqlalchemy as orm

from app.context import AppContext, function_context
from app.models import Consumption, Product


@function_context
def needs_to_consume(
    ctx: AppContext, id: int, product_category: str, norm: int, time_offset: timedelta
) -> int:
    suitable_products = ctx.database.session.scalars(orm.select(Product.id).filter(Product.category == product_category)).all()

    consumed = ctx.database.session.scalars(
        orm.select(Consumption).filter(orm.and_(Consumption.bank_account_id == id, Consumption.product_id.in_(suitable_products)))
    ).all()

    if consumed is None:
        return norm

    total = 0
    for entry in consumed:
        if (entry.consumed_at + time_offset).date() > datetime.now().date():
            total += entry.count

    if total < norm:
        return norm - total
    return 0
