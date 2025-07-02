import csv
import sqlalchemy as orm

from datetime import datetime
from io import StringIO

from app.api import Blueprints
from app.api.bulk import bulk
from app.context import AppContext
from app.models import Product, User, Prefecture
from app.models.queries import CRUD, wrap_crud_context


@Blueprints.loader.route("/api/bulk/users", methods=["POST"])
@bulk.bulk
def bulk_create_users(ctx: AppContext, stream: StringIO):
    with wrap_crud_context():
        money = ctx.database.session.get(Product, 1)
        if money is None:
            ctx.logger.info("MONEY product not found, adding")
            ctx.database.session.add(Product("MONEY", "надик", 1))
            ctx.database.session.commit()

        for row in csv.DictReader(stream, delimiter=";"):
            try:
                prefecture_name = row.get("Prefecture")
                prefecture = None
                if prefecture_name:
                    prefecture = ctx.database.session.scalar(
                        orm.select(Prefecture).filter(Prefecture.name == prefecture_name)
                    )
                    if prefecture is None:
                        raise ValueError(f"Prefecture '{prefecture_name}' not found for user: {row}")

                user = User(
                    birthday=datetime.strptime(row["Birthday"], "%d.%m.%Y"),
                    bank_account_id=None,
                    prefecture_id=prefecture.id,
                    name=row["Name"],
                    last_name=row["Surname"],
                    patronymic=row["Patronymic"],
                    login=row["Login"],
                    password=row["Password"],
                    sex=row["Sex"],
                    bonus=int(row["Bonus"]),
                    is_admin=row["IsAdmin"].lower() == "true",
                )

                CRUD.create_user(user)
                ctx.database.session.commit()

            except KeyError as err:
                ctx.logger.error(f"bad CSV line: {row}; missing column: {err}")
                raise
            except ValueError as err:
                ctx.logger.error(f"bad CSV line: {row}; value error: {err}")
                raise

        return "success", 200

    return "bulk adding failed", 400
