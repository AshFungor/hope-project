import sqlalchemy as orm

from typing import List, Tuple, Union
from datetime import timedelta, datetime

from app.models import Product, Consumption
from app.context import function_context, AppContext

@function_context
def get_all_products(ctx: AppContext) -> List[Product]:
    ctx.database.session.scalars(
        orm.select(Product)
    ).all()

@function_context
def did_consume_enough(
    ctx: AppContext, id: int,product_category: str, norm: int, time_offset: timedelta
) -> Union[Tuple[bool, str], Tuple[bool, int]]:
    suitable_products = ctx.database.session.scalars(
        orm
        .select(Product.id)
        .filter(Product.category == product_category)
    ).all()

    consumed = ctx.database.session.scalars(
        orm
        .select(Consumption)
        .filter(
            orm.and_(
                Consumption.bank_account_id == id,
                Consumption.product_id.in_(suitable_products)
            )
        )
    ).all()

    if consumed is None:
        return False, f'в этот день категория {product_category} не употреблялся'
    
    total = 0
    for entry in consumed:
        if (entry.consumed_at + time_offset).date() > datetime.now().date():
            total += entry.count

    if total < norm:
        return False, norm - total
    return True, 0