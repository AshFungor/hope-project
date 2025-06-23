import datetime
import logging

import flask
import sqlalchemy
from flask import Blueprint, render_template, url_for
from flask_login import current_user, login_required

import app.models as models

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints
from app.env import env
from app.modules.database.validators import CurrentTimezone


@blueprints.accounts_blueprint.route("/master_lk")
@login_required
def master_cabinet():
    """Личный кабинет мастера"""
    return render_template("main/master_lk.html")


@blueprints.master_blueprint.route("/edit_data")
@login_required
def edit_data():
    """Мастер изменяет данные"""
    return render_template("main/master_edit.html")


@blueprints.master_blueprint.route("/action_with_resource", methods=["POST"])
@login_required
def action_with_product():
    # check input data
    try:
        form_id = int(flask.request.form.get("form_id", None))
    except ValueError as Error:
        logging.warning(f"{Error} ")
        return flask.Response("Ошибка при добавлении продукта", status=400)
    if form_id is None:
        return flask.Response("Ошибка при добавлении продукта", status=400)
    try:
        data = {
            "количество": int(flask.request.form.get("count", None)),
            "сумма": int(flask.request.form.get("amount", None)),
            "название товара": flask.request.form.get("name", None).strip().lower(),
            "счет": int(flask.request.form.get("bank_account", None)),
        }
    except Exception:
        return flask.Response("Ошибка при преобразовании данных", status=400)

    # execute data from database
    product = env.db.impl().session.execute(sqlalchemy.select(models.Product).filter_by(name=data["название товара"])).scalars().first()
    if product is None:
        logging.warning(f"при действии мастера с товаром произошла ошибка: продукт не найден")
        return flask.Response("Продукт не найден", 400)

    # checking for the existence of bank_account
    check_bank_account = env.db.impl().session.execute(sqlalchemy.select(models.BankAccount).filter_by(id=data["счет"])).first()
    if check_bank_account is None:
        logging.warning(f"при действии мастера с товаром произошла ошибка: счет не найден")
        return flask.Response("введенный счет не был найден", 400)
    products2bank_account = (
        env.db.impl()
        .session.execute(
            sqlalchemy.select(models.Product2BankAccount).filter(
                sqlalchemy.and_(models.Product2BankAccount.product_id == product.id, models.Product2BankAccount.bank_account_id == data["счет"])
            )
        )
        .scalars()
        .first()
    )
    if products2bank_account is None:
        products2bank_account = models.Product2BankAccount(bank_account_id=int(data["счет"]), product_id=product.id, count=0)
        env.db.impl().session.add(products2bank_account)
        env.db.impl().session.commit()
    customer_wallet = (
        env.db.impl()
        .session.execute(sqlalchemy.select(models.Product2BankAccount).filter_by(bank_account_id=data["счет"], product_id=1))
        .scalars()
        .first()
    )
    if form_id == 3:
        products2bank_account.count = products2bank_account.count - data["количество"]
        customer_wallet.count += data["сумма"]
    elif form_id == 4:
        products2bank_account.count += data["количество"]
        customer_wallet.count = customer_wallet.count - data["сумма"]
    if customer_wallet.count < 0:
        env.db.impl().session.rollback()
        return flask.Response("У покупателя недостаточно надиков", 400)
    try:
        transaction = models.Transaction(
            product.id,
            int(data["счет"]),
            current_user.bank_account_id,
            int(data["количество"]),
            amount=data["сумма"],
            status="approved",
            created_at=datetime.datetime.now(tz=CurrentTimezone),
            updated_at=datetime.datetime.now(tz=CurrentTimezone),
            comment=f'мастер перевел/списал продукт {product.name} на счет {data["счет"]} в количестве {data["количество"]}',
        )
        logging.info(f'мастер перевел/списал продукт {product.name} на счет {data["счет"]} в количестве {data["количество"]}')
        env.db.impl().session.add(transaction)
        env.db.impl().session.commit()
    except Exception as Error:
        env.db.impl().session.rollback()
        flask.Response(f"Произошла ошибка во время выполнения действия", 400)
        logging.warning(f"{Error}")
    return render_template("main/add_withdrowal.html", products=models.Product.get_all())


@blueprints.master_blueprint.route("/master_add_money", methods=["POST"])
@login_required
def add_money():
    try:
        data = {
            "форма": int(flask.request.form.get("form_id", None)),
            "счет": int(flask.request.form.get("bank_account", None)),
            "количество": int(flask.request.form.get("count", None)),
        }
    except Exception as Error:
        logging.warning("ошибка при получении данных")
        return flask.Response("Ошибка при добавлении надиков", 400)
    user_wallet = (
        env.db.impl()
        .session.execute(sqlalchemy.select(models.Product2BankAccount).filter_by(bank_account_id=data["счет"], product_id=1))
        .scalars()
        .first()
    )
    if user_wallet is None:
        logging.warning(f"При добавлении мастером {current_user.bank_account_id} надиков не был найден кошелек пользователя")
        return flask.Response("Не был найден счет", 400)

    if data["форма"] == 1:
        user_wallet.count -= data["количество"]
    elif data["форма"] == 2:
        user_wallet.count += data["количество"]
    try:
        transaction = models.Transaction(
            product_id=1,
            customer_bank_account_id=current_user.bank_account_id,
            seller_bank_account_id=data["счет"],
            count=data["количество"],
            amount=data["количество"],
            status="approved",
            created_at=datetime.datetime.now(tz=CurrentTimezone),
            updated_at=datetime.datetime.now(tz=CurrentTimezone),
            comment=f'мастер {current_user.bank_account_id} перевел продукт надики на счет {data["счет"]} в количестве {data["количество"]}',
        )
        logging.info(f'мастер {current_user.bank_account_id} перевел продукт надики на счет {data["счет"]} в количестве {data["количество"]}')
        env.db.impl().session.add(transaction)
        env.db.impl().session.commit()
    except Exception as Error:
        env.db.impl().session.rollback()
        logging.warning(
            f'При пропытке добавить надики мастером {current_user.bank_account_id} на счет {data["счет"]} в количестве {data["количество"]}'
        )
        return flask.Response("при попытке добавить надики произошла ошибка")
    return render_template("main/add_withdrowal.html", products=models.Product.get_all())


@blueprints.master_blueprint.route("/create_office", methods=["POST"])
@login_required
def create_office():
    office_data = {
        "company_account": int(flask.request.form.get("company_bank_account", None)),
        "city_name": flask.request.form.get("city_bank_account", None),
        "amount": int(flask.request.form.get("amount", None)),
    }

    # checks
    for key, value in office_data.items():
        if office_data[key] is None:
            logging.warning(f"missing field: {key}")
            return flask.Response("Не удалось получить данные", status=400)

    city = env.db.impl().session.execute(sqlalchemy.select(models.City).filter_by(name=office_data["city_name"])).scalars().first()
    if city is None:
        logging.warning(f'City {office_data["city_name"]} was not found')
        return flask.Response("Город не был найден. Проверьте правильность введенных данных.", status=400)

    company = (
        env.db.impl()
        .session.execute(sqlalchemy.select(models.Company).filter(models.Company.bank_account_id == office_data["company_account"]))
        .scalars()
        .first()
    )
    logging.info(f'{office_data["company_account"]}')
    if company is None:
        logging.warning(f'Company {office_data["company_account"]} was not found')
        return flask.Response("Компания не была найдена. Проверьте правильность введенных данных.", status=400)

    company_wallet = (
        env.db.impl()
        .session.execute(
            sqlalchemy.select(models.Product2BankAccount).filter(
                sqlalchemy.and_(
                    models.Product2BankAccount.bank_account_id == office_data["company_account"], models.Product2BankAccount.product_id == 1
                )
            )
        )
        .scalars()
        .first()
    )

    company_wallet.count = company_wallet.count - office_data["amount"]
    if company_wallet.count < 0:
        env.db.impl().session.rollback()
        logging.warning(f'The company ({office_data["company_account"]}) does not have money for an office')
        return flask.Response("У данной компании нет денег на счету для покупки офиса.", status=400)
    # create office
    office = models.Office(city_id=city.id, company_id=company.id, founded_at=datetime.datetime.now(tz=CurrentTimezone))
    env.db.impl().session.add(office)
    env.db.impl().session.commit()
    logging.info(f"матстер {current_user.bank_account_id} добавил офис в городе {city.name} для компании {company.name}")

    return render_template("main/create_office.html", cities=models.City.get_all())
