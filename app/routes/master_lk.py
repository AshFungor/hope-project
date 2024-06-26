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
    name = flask.request.form.get('name', None)
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


