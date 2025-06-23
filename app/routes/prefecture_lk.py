import copy
import logging
import typing

import flask
import flask_login
import sqlalchemy as orm

import app.models as models
import app.modules.statistics.excluders as excluders
import app.routes.blueprints as blueprints
import app.routes.person_account as account
from app.env import env


def assistant_visitor(assistants: list[str], prefecture: models.Prefecture) -> dict[str, models.User]:
    result = {}
    for assistant in assistants:
        user = env.db.impl().session.execute(orm.select(models.User).where(models.User.id == getattr(prefecture, assistant))).scalars().first()
        result[assistant] = user
    return result


def get_current_roles(assistants: dict[str, models.User], soft_names: list[str], current_user: models.User) -> dict[str, bool]:
    return {soft: user and current_user.id == user.id for user, soft in zip(assistants.values(), soft_names)}


def decorate_city(city: models.City, prefecture: models.Prefecture, money: models.Product2BankAccount) -> models.City:
    city = copy.deepcopy(city)
    setattr(city, "minus", abs(money.count))
    setattr(city, "prefecture_name", prefecture.name)
    return city


def get_bankrupt_cities(prefecture_id: int | None = None) -> list[models.City]:
    return [
        decorate_city(city, prefecture, money)
        for city, prefecture, money in env.db.impl()
        .session.query(models.City, models.Prefecture, models.Product2BankAccount)
        .join(models.Product2BankAccount, models.Product2BankAccount.bank_account_id == models.City.bank_account_id)
        .join(models.Prefecture, models.Prefecture.id == models.City.prefecture_id)
        .filter(
            orm.and_(
                (models.City.prefecture_id == prefecture_id if prefecture_id is not None else True),
                models.Product2BankAccount.count < 0,
                models.Product2BankAccount.product_id == 1,
                models.City.bank_account_id.not_in(excluders.high_rule()),
            )
        )
        .all()
    ]


def decorate_company(company: models.Company, money: models.Product2BankAccount) -> models.Company:
    company = copy.deepcopy(company)
    setattr(company, "minus", abs(money.count))
    return company


def get_bankrupt_companies(prefecture_id: int | None = None) -> list[models.Company]:
    return [
        decorate_company(company, money)
        for company, money in env.db.impl()
        .session.query(models.Company, models.Product2BankAccount)
        .join(models.Product2BankAccount, models.Product2BankAccount.bank_account_id == models.Company.bank_account_id)
        .filter(
            orm.and_(
                (models.Company.prefecture_id == prefecture_id if prefecture_id is not None else True),
                models.Product2BankAccount.count < 0,
                models.Product2BankAccount.product_id == 1,
                models.Company.bank_account_id.not_in(excluders.high_rule()),
            )
        )
        .all()
    ]


def decorate_user(user: models.User, city: models.City, money: models.Product2BankAccount) -> models.User:
    user = copy.deepcopy(user)
    setattr(user, "city_name", city.name)
    setattr(user, "city_location", city.location)
    setattr(user, "minus", abs(money.count))
    return user


def get_bankrupt_users(prefecture_id: int | None = None) -> list[models.User]:
    return [
        decorate_user(user, city, money)
        for user, city, money in env.db.impl()
        .session.query(models.User, models.City, models.Product2BankAccount)
        .join(models.User, models.City.id == models.User.city_id)
        .join(models.Prefecture, models.Prefecture.id == models.City.prefecture_id)
        .join(models.Product2BankAccount, models.Product2BankAccount.bank_account_id == models.User.bank_account_id)
        .filter(
            orm.and_(
                (models.Prefecture.id == prefecture_id if prefecture_id is not None else True),
                models.Product2BankAccount.count < 0,
                models.Product2BankAccount.product_id == 1,
                models.User.bank_account_id.not_in(excluders.high_rule()),
            )
        )
        .all()
    ]


def query_bankrupts(territory: str, id: int) -> typing.Tuple[list[models.User], list[models.Company], list[models.City]]:
    if territory.lower().startswith("prefecture"):
        return (get_bankrupt_users(id), get_bankrupt_companies(id), get_bankrupt_cities(id))
    return (get_bankrupt_users(), get_bankrupt_companies(), get_bankrupt_cities())


@blueprints.accounts_blueprint.route("/prefecture_account")
@flask_login.login_required
def prefecture_cabinet():
    current_user = copy.deepcopy(flask_login.current_user)
    city = env.db.impl().session.query(models.City).get(current_user.city_id)
    prefecture = env.db.impl().session.query(models.Prefecture).get(city.prefecture_id)

    roles = {
        "economic_assistant": "заместитель по экономической политике",
        "social_assistant": "заместитель по социальной политике",
        "prefect": "префект",
    }
    visitor = assistant_visitor(["economic_assistant_id", "social_assistant_id", "prefect_id"], prefecture)
    current_role = get_current_roles(visitor, roles.keys(), current_user)

    goal = models.Goal.get_last(prefecture.bank_account_id, True)
    if current_role["prefect"] and goal is None:
        return flask.redirect(flask.url_for("goal_view.view_create_goal", account=prefecture.bank_account_id))

    if goal:
        setattr(goal, "rate", goal.get_rate(account.get_money(prefecture.bank_account_id)))
    setattr(prefecture, "money", account.get_money(prefecture.bank_account_id))
    balance = account.get_money(prefecture.id)

    specs = []
    for visited, name in zip(visitor, roles.keys()):
        setattr(prefecture, name, visitor[visited])

    mapper = {"bank_account_id": "номер банковского счета", **roles}

    for spec in mapper:
        specs.append({"name": mapper[spec], "value": getattr(prefecture, spec)})

    bankrupt_users, bankrupt_companies, bankrupt_cities = query_bankrupts("prefecture", prefecture.id)

    return flask.render_template(
        "main/prefecture_lk_page.html",
        user_spec=specs,
        goal=goal,
        balance=balance,
        prefecture=prefecture,
        roles=current_role,
        bankrupt_users=bankrupt_users,
        bankrupt_companies=bankrupt_companies,
        bankrupt_cities=bankrupt_cities,
    )
