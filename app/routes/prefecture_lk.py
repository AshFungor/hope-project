import copy
import typing
import logging

import flask
import flask_login

import sqlalchemy as orm

from app.env import env
import app.models as models
import app.routes.blueprints as blueprints
import app.routes.person_account as account


def assistant_visitor(
    assistants: list[str], 
    prefecture: models.Prefecture
) -> dict[str, models.User]:
    result = {}
    for assistant in assistants:
        user = env.db.impl().session.execute(
            orm.select(models.User).where(models.User.id == getattr(prefecture, assistant))
        ).scalars().first()
        result[assistant] = user
    return result


def get_current_roles(
    assistants: dict[str, models.User],
    soft_names: list[str],
    current_user: models.User
) -> dict[str, bool]:
    return {soft: user and current_user.id == user.id for user, soft in zip(assistants.values(), soft_names)}


def decorate_user(user: models.User, city: models.City, money: models.Product2BankAccount) -> models.User:
    user = copy.deepcopy(user)
    setattr(user, 'city_name', city.name)
    setattr(user, 'minus', abs(money.count))
    return user


def decorate_company(company: models.Company, money: models.Product2BankAccount) -> models.Company:
    company = copy.deepcopy(company)
    setattr(company, 'minus', abs(money.count))
    return company


def query_bankrupts(territory: str, id: int) -> typing.Tuple[list[models.User], list[models.Company]] | list[models.Company]:
    if territory.lower().startswith('prefecture'):
        companies = [decorate_company(company, money) for company, money in env.db.impl().session
            .query(models.Company, models.Product2BankAccount)
            .join(models.Product2BankAccount, models.Product2BankAccount.bank_account_id == models.Company.bank_account_id)
            .filter(orm.and_(
                models.Company.prefecture_id == id,
                models.Product2BankAccount.count < 0,
                models.Product2BankAccount.product_id == 1
            )
        ).all()]
        users = [decorate_user(user, city, money) for user, city, money in env.db.impl().session
            .query(models.User, models.City, models.Product2BankAccount)
            .join(models.User, models.City.id == models.User.city_id)
            .join(models.Prefecture, models.Prefecture.id == models.City.prefecture_id)
            .join(models.Product2BankAccount,
                models.Product2BankAccount.bank_account_id == models.User.bank_account_id
            )
            .filter(orm.and_(
                models.Product2BankAccount.count < 0,
                models.Prefecture.id == id,
                models.Product2BankAccount.product_id == 1
            )
        ).all()]
        return (users, companies)
    # get all users
    companies = [decorate_company(company, money) for company, money in env.db.impl().session
        .query(models.Company, models.Product2BankAccount)
        .join(models.Product2BankAccount, models.Product2BankAccount.bank_account_id == models.Company.bank_account_id)
        .filter(orm.and_(
            models.Product2BankAccount.count < 0,
            models.Product2BankAccount.product_id == 1
        )
    ).all()]
    users = [decorate_user(user, city, money) for user, city, money in env.db.impl().session
        .query(models.User, models.City, models.Product2BankAccount)
        .join(models.User, models.City.id == models.User.city_id)
        .join(models.Prefecture, models.Prefecture.id == models.City.prefecture_id)
        .join(models.Product2BankAccount,
            models.Product2BankAccount.bank_account_id == models.User.bank_account_id
        )
        .filter(orm.and_(
            models.Product2BankAccount.count < 0,
            models.Product2BankAccount.product_id == 1
        )
    ).all()]
    return (users, companies)


@blueprints.accounts_blueprint.route('/prefecture_account')
@flask_login.login_required
def prefecture_cabinet():
    current_user = copy.deepcopy(flask_login.current_user)
    city = env.db.impl().session.query(models.City).get(current_user.city_id)
    prefecture = env.db.impl().session.query(models.Prefecture).get(city.prefecture_id)

    roles = {
        'economic_assistant': 'заместитель по экономической политике',
        'social_assistant': 'заместитель по социальной политике',
        'prefect': 'префект'
    }
    visitor = assistant_visitor(
        ['economic_assistant_id', 'social_assistant_id', 'prefect_id'],
        prefecture
    )
    current_role = get_current_roles(visitor, roles.keys(), current_user)

    goal = models.Goal.get_last(prefecture.bank_account_id, True)
    if current_role['prefect'] and goal is None:
        return flask.redirect(flask.url_for('goal_view.view_create_goal', account=prefecture.bank_account_id))

    if goal:
        setattr(goal, 'rate', goal.get_rate(account.get_money(prefecture.bank_account_id)))
    setattr(prefecture, 'money', account.get_money(prefecture.bank_account_id))
    balance = account.get_money(prefecture.id)

    specs = []
    for visited, name in zip(visitor, roles.keys()):
        setattr(prefecture, name, visitor[visited])

    mapper = {
        'bank_account_id': 'номер банковского счета',
        **roles
    }

    for spec in mapper:
        specs.append({'name': mapper[spec], 'value': getattr(prefecture, spec)})

    bankrupt_users, bankrupt_companies = query_bankrupts('prefecture', prefecture.id)

    return flask.render_template(
        'main/prefecture_lk_page.html', 
        user_spec=specs, 
        goal=goal, 
        balance=balance,
        prefecture=prefecture,
        roles=current_role,
        bankrupt_users=bankrupt_users,
        bankrupt_companies=bankrupt_companies
    )
