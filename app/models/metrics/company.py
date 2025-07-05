from datetime import datetime, timedelta
from typing import Optional

import sqlalchemy as orm

from app.context import AppContext, class_context
from app.models import BankAccount, Company, Product, Transaction


class CompanyMetrics:
    """
    Metrics are prone to changes, take as reference.
    """

    __ctx = AppContext.safe_load()

    @classmethod
    def __get_income_for_category(cls, category: str, span: Optional[timedelta]) -> dict:
        result = cls.__ctx.database.session.execute(
            orm.select(orm.func.sum(Transaction.count), Company.name)
            .join(Product, Product.id == Transaction.product_id)
            .join(Company, Company.bank_account_id == Transaction.seller_bank_account_id)
            .filter(
                orm.and_(
                    orm.cast(Transaction.seller_bank_account_id, orm.String).startswith(str(cls.__ctx.config.account_mapping.company)),
                    Transaction.product_id != cls.__ctx.config.money_product_id,
                    Product.category == category,
                    span and Transaction.updated_at >= datetime.now() - span,
                )
            )
            .group_by(Company.id)
        ).all()

        data = {
            "companies": [],
            "income": [],
        }

        for s, name in result:
            data["companies"].append(name)
            data["income"].append(s)

        return data

    @classmethod
    def get_total_income(cls):
        categories = cls.__ctx.database.session.scalars(orm.select(Product.category).distinct())

        data = {"category": categories, "data": []}

        for category in categories:
            current = cls.__get_income_for_category(category)
            data["data"].append(current)

        return data
