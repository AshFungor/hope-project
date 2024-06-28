import datetime
import logging
import flask
from flask import Blueprint, render_template, url_for
from flask_login import login_required
import sqlalchemy

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints
import app.models as models
from app.env import env
from app.modules.database.validators import CurrentTimezone


@blueprints.accounts_blueprint.route('/master_lk')
@login_required
def master_cabinet():
    """Личный кабинет мастера"""
    return render_template('main/master_lk.html')

@blueprints.master_blueprint.route('/edit_data')
@login_required
def edit_data():
    """Мастер изменяет данные"""
    return render_template('main/master_edit.html')


@blueprints.master_blueprint.route('/action_with_products', methods=['POST'])
@login_required
def action_with_energy():
    try:
        form_id = int(flask.request.form.get('form_id', None))
    except Exception as Error:
        logging.warning(f'{Error}')
        return flask.Response(
            'Ошибка при добавлении энергии',
            status=400
        )
    if form_id is None:
        return flask.Response(
            'Ошибка при добавлении энергии',
            status=400
        )
    count = flask.request.form.get('count', None)
    bank_account = flask.request.form.get('bank_account', None)
    if None in (count, bank_account):
        return flask.Response(
            'Ошибка получения данных',
            status=400
        )
    product_id = env.db.impl().session.execute(
        sqlalchemy.select(
            models.Product.id
        )
        .filter_by(name='энергия')
    ).scalars().first()
    if product_id is None:
        return flask.Response(
            'Энергия не найдена'
        )
    check_bank_account = env.db.impl().session.execute(
        sqlalchemy.select(
            models.BankAccount
        )
        .filter_by(id=bank_account)
    ).first()
    if not check_bank_account:
        return flask.Response(
            'такого счета не существует',
            400
        )
    products2bank_account = env.db.impl().session.execute(
        sqlalchemy.select(
            models.Product2BankAccount
        )
        .filter(sqlalchemy.and_(
            models.Product2BankAccount.product_id == product_id,
            models.Product2BankAccount.bank_account_id == bank_account
        ))
    ).scalars().first()
    if products2bank_account is None:
        products2bank_account = models.Product2BankAccount(
            bank_account_id=int(bank_account),
            product_id=product_id,
            count=0
        )
        env.db.impl().session.add(products2bank_account)
        env.db.impl().session.commit()
    if form_id == 1:
        products2bank_account.count = products2bank_account.count - int(count)
    elif form_id == 2:
        products2bank_account.count += int(count)
    try:
        env.db.impl().session.commit()
    except Exception as Error:
        flask.Response(
            f'Произошла ошибка во время выполнения действия',
            400
        )
        logging.warning(f'{Error}')
    return render_template('main/add_withdrowal.html')


@blueprints.master_blueprint.route('/action_with_resource', methods=['POST'])
@login_required
def action_with_resource():
    try:
        form_id = int(flask.request.form.get('form_id', None))
    except Exception as Error:
        logging.warning(f'{Error}')
        return flask.Response(
            'Ошибка при добавлении энергии',
            status=400
        )
    if form_id is None:
        return flask.Response(
            'Ошибка при добавлении энергии',
            status=400
        )
    count = int(flask.request.form.get('count', None))
    name = flask.request.form.get('name', None).strip()
    bank_account = flask.request.form.get('bank_account', None)
    if None in (count, bank_account, name):
        return flask.Response(
            'Ошибка получения данных',
            status=400
        )
    product_id = env.db.impl().session.execute(
        sqlalchemy.select(
            models.Product.id
        )
        .filter_by(name=name)
    ).scalars().first()
    if product_id is None:
        return flask.Response(
            'Продукт или ресурс не найден'
        )
    check_bank_account = env.db.impl().session.execute(
        sqlalchemy.select(
            models.BankAccount
        )
        .filter_by(id=bank_account)
    ).first()
    if not check_bank_account:
        return flask.Response(
            'такого счета не существует',
            400
        )
    products2bank_account = env.db.impl().session.execute(
        sqlalchemy.select(
            models.Product2BankAccount
        )
        .filter(sqlalchemy.and_(
            models.Product2BankAccount.product_id == product_id,
            models.Product2BankAccount.bank_account_id == bank_account
        ))
    ).scalars().first()
    if products2bank_account is None:
        products2bank_account = models.Product2BankAccount(
            bank_account_id=int(bank_account),
            product_id=product_id,
            count=0
        )
        env.db.impl().session.add(products2bank_account)
        env.db.impl().session.commit()
    if form_id in (3, 5):
        products2bank_account.count = products2bank_account.count - int(count)
    elif form_id in (4, 6):
        products2bank_account.count += count
    try:
        env.db.impl().session.commit()
    except Exception as Error:
        flask.Response(
            f'Произошла ошибка во время выполнения действия',
            400
        )
        logging.warning(f'{Error}')
    return render_template('main/add_withdrowal.html')


@blueprints.master_blueprint.route('/create_office', methods=['POST'])
@login_required
def create_office():
    office_data = {
        'company_account': int(flask.request.form.get('company_bank_account', None)),
        'city_name': flask.request.form.get('city_bank_account', None).capitalize(),
        'amount': int(flask.request.form.get('amount', None))
    }

    # checks
    for key, value in office_data.items():
        if office_data[key] is None:
            logging.warning(f'missing field: {key}')
            return flask.Response(
                'Не удалось получить данные',
                status=400
            )

    city = env.db.impl().session.execute(
        sqlalchemy.select(
            models.City
        )
        .filter_by(name=office_data['city_name'])
    ).scalars().first()
    if city is None:
        logging.warning(f'City {office_data["city_name"]} was not found')
        return flask.Response(
            'Город не был найден. Проверьте правильность введенных данных.',
            status=400
        )

    company = env.db.impl().session.execute(
        sqlalchemy.select(
            models.Company
        )
        .filter(models.Company.bank_account_id == office_data['company_account'])
    ).scalars().first()
    logging.info(f'{office_data["company_account"]}')
    if company is None:
        logging.warning(f'Company {office_data["company_account"]} was not found')
        return flask.Response(
            'Компания не была найдена. Проверьте правильность введенных данных.',
            status=400
        )

    company_wallet = env.db.impl().session.execute(
        sqlalchemy.select(
            models.Product2BankAccount
        )
        .filter(
            sqlalchemy.and_(
                models.Product2BankAccount.bank_account_id == office_data['company_account'],
                models.Product2BankAccount.product_id == 1
            )
        )
    ).scalars().first()

    company_wallet.count = company_wallet.count - office_data['amount']
    if company_wallet.count < 0:
        env.db.impl().session.rollback()
        logging.warning(f'The company ({office_data["company_account"]}) does not have money for an office')
        return flask.Response(
            'У данной компании нет денег на счету для покупки офиса.',
            status=400
        )
    # create office
    office = models.Office(
        city_id=city.id,
        company_id=company.id,
        founded_at=datetime.datetime.now(tz=CurrentTimezone)
    )
    env.db.impl().session.add(office)
    env.db.impl().session.commit()

    return render_template('main/create_office.html')
