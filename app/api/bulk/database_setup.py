import sqlalchemy as orm

from datetime import datetime

from app.api import Blueprints
from app.context import AppContext, function_context
from app.models import BankAccount, Product, CityHall, User, Sex, Prefecture
from app.models.queries import CRUD, wrap_crud_context


@function_context
def query_admin_account(ctx: AppContext) -> User:
    admin = ctx.database.session.execute(
        orm.select(User).filter(User.name == "Магистрат")
    ).scalar_one_or_none()

    if admin is None:
        ctx.logger.info("missing admin account, setting it up")
        return CRUD.create_user(
            User(
                birthday=datetime.now(),
                bank_account_id=None,
                prefecture_id=None,
                name="Магистрат",
                last_name="Города",
                patronymic="Надежда",
                login="login",
                password="password",
                sex=Sex.MALE,
                bonus=0,
                is_admin=True,
            )
        )
    return admin


@Blueprints.loader.route("/api/bulk/products")
@function_context
def setup_products(ctx: AppContext):
    with wrap_crud_context():
        money = ctx.database.session.get(Product, 1)
        if money is None:
            ctx.logger.info("money does not exist, adding product with id = 1")
            ctx.database.session.add(Product("MONEY", "надик", 0))
            ctx.database.session.commit()

    return "ok", 200


@Blueprints.loader.route("/api/bulk/city_hall")
@function_context
def setup_city_hall(ctx: AppContext):
    with wrap_crud_context():
        city_hall = ctx.database.session.get(CityHall, 1)
        if city_hall is None:
            ctx.logger.info("city hall is missing, setting it up")

            admin = query_admin_account()
            account = CRUD.create_bank_account(BankAccount.AccountMapping.CITY_HALL)
            ctx.database.session.add(
                CityHall(
                    bank_account_id=account,
                    mayor_id=admin.id,
                    economic_assistant_id=admin.id,
                    social_assistant_id=admin.id
                )
            )
            ctx.database.session.commit()

    return "ok", 200


@Blueprints.loader.route("/api/bulk/prefectures")
@function_context
def setup_prefectures(ctx: AppContext):
    with wrap_crud_context():
        admin = query_admin_account()
        names = ["Южная", "Северная", "Восточная", "Западная"]

        for name in names:
            exists = ctx.database.session.scalar(
                orm.select(Prefecture).filter(Prefecture.name == name)
            )
            if exists:
                ctx.logger.info(f"Prefecture '{name}' already exists, skipping")
                continue

            account = CRUD.create_bank_account(BankAccount.AccountMapping.PREFECTURE)

            new_prefecture = Prefecture(
                name=name,
                bank_account_id=account,
                prefect_id=admin.id,
                economic_assistant_id=admin.id,
                social_assistant_id=admin.id,
            )
            ctx.database.session.add(new_prefecture)
            ctx.logger.info(f"Prefecture '{name}' created")

        ctx.database.session.commit()
        ctx.logger.info("Prefecture setup complete")
    
    return "ok", 200


@Blueprints.loader.route("/api/bulk/all")
@function_context
def setup_all(ctx: AppContext):
    ctx.logger.info("Bulk setup: starting all setup steps")

    setup_products()
    # setup_city_hall()
    setup_prefectures()

    ctx.logger.info("Bulk setup: all steps completed")
    return "ok", 200
