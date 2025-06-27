import csv

from io import StringIO
from datetime import datetime

from app.api.bulk import bulk
from app.api import Blueprints
from app.context import AppContext
from app.models.queries import wrap_crud_context
from app.models import User, BankAccount, Product2BankAccount, Product


# TODO: fix this
@Blueprints.loader.route("/api/bulk/users", methods=["POST"])
@bulk
def bulk_create_users(ctx: AppContext, stream: StringIO):
    with wrap_crud_context():
        money = ctx.database.session.get(Product, 1)
        if money is None:
            ctx.database.session.add(
                Product("MONEY", "надик", 1)
            )
            ctx.database.session.commit()

        for row in csv.DictReader(stream, delimiter=';'):
            generated = BankAccount.from_kind(BankAccount.AccountMapping.USER)
            account = BankAccount(generated)

            try:
                user = User(
                    birthday=datetime.strptime(row["Birthday"], "%d.%m.%Y"),
                    bank_account_id=generated,
                    prefecture_id=None,
                    name=row["Name"],
                    last_name=row["Surname"],
                    patronymic=row["Patronymic"],
                    login=row["Login"],
                    password=row["Password"],
                    sex=row["Sex"],
                    bonus=int(row["Bonus"]),
                    is_admin=row["IsAdmin"].lower() in ("true", "1", "yes"),
                )
            except KeyError as err:
                ctx.logger.error(f"bad line: {row}; error: {err}")
                raise

            link = Product2BankAccount(generated, 1, 0)
            ctx.database.session.add_all([account, user, link])

        ctx.database.session.commit()
        return "success", 200
    
    return "bulk adding failed", 400
