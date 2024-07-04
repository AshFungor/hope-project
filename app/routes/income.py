import io
import base64
import typing
import logging
import datetime

import flask
import flask_login

import scipy.stats as stat
import sklearn.preprocessing as learn

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import sqlalchemy as orm

import app.models as models
import app.modules.database.validators as validators
import app.routes.blueprints as blueprints
import app.routes.person_account as accounts
import app.modules.statistics.common as common
import app.modules.statistics.excluders as exclude
import app.routes.consumption as consumption

from app.env import env


def select_consumption_total(
    id: int,
    offset: datetime.timedelta,
    auto_lower: datetime.time = datetime.time(hour=20),
    auto_margin: datetime.timedelta = datetime.timedelta(hours=4) - \
        datetime.timedelta.resolution
) -> list[int]:
    if (datetime.datetime.combine(datetime.date.today(), auto_lower) 
        + auto_margin).time() < auto_lower:
        raise ValueError(f'upper should not exceed 1 day')
    return [consumption.defaults[product.category] * consumed.count
        for consumed, product in 
        env.db.impl().session.query(
            models.Consumption,
            models.Product
        ).join(
            models.Product,
            models.Product.id == models.Consumption.product_id
        ).filter(
            orm.and_(
                models.Consumption.bank_account_id == id,
                models.Consumption.consumed_at \
                    >= (datetime.datetime.now() - offset),
                orm.cast(models.Consumption.consumed_at, orm.Time) \
                    >= auto_lower,
                orm.cast(models.Consumption.consumed_at, orm.Time) \
                    <= (datetime.datetime.combine(
                        datetime.date.today(), auto_lower
                    ) + auto_margin).time()
            )
        ).all()
    ]


def select_spending_total(
    id: int,
    offset: datetime.timedelta
) -> list[int]:
    return [transaction.amount 
        for transaction in env.db.impl().session.query(
            models.Transaction
        ).filter(
            orm.and_(
                models.Transaction.seller_bank_account_id == id,
                models.Transaction.updated_at \
                    >= (datetime.datetime.now() - offset),
                models.Transaction.status == 'approved'
            )
        ).all()
    ]


def select_gain_total(
    id: int,
    offset: datetime.timedelta
) -> list[int]:
    return [transaction.amount 
        for transaction in env.db.impl().session.query(
            models.Transaction
        ).filter(
            orm.and_(
                models.Transaction.customer_bank_account_id == id,
                models.Transaction.updated_at \
                    >= (datetime.datetime.now() - offset),
                models.Transaction.status == 'approved'
            )
        ).all()
    ]


def restore_account_delta(
    id: int,
    offset: datetime.timedelta,
    *query_args: any
) -> int:
    consumed = np.sum(select_consumption_total(id, offset, *query_args))
    spent = np.sum(select_spending_total(id, offset, *query_args))
    gained = np.sum(select_gain_total(id, offset, *query_args))
    return gained - consumed - spent


def calculate_total_market_share(
    include_bankrupts: bool = False,
    offset: datetime.timedelta | None = None
) -> list[typing.Tuple[int, int]]:
    '''
    Calculate total money share in the market excluding admins accounts
    and money, expired on external market
    Returns mappings for accounts with individual share 
    '''
    if offset is None:
        offset = datetime.timedelta(days=0)
    return np.asarray(
        [(
            account.bank_account_id,
            account.count - restore_account_delta(
                account.bank_account_id, offset
            )
        )
        for account in
            env.db.impl().session.query(
                models.Product2BankAccount,
            ).filter(
                orm.and_(
                    (
                        orm.true if include_bankrupts else 
                        models.Product2BankAccount.count >= 0
                    ),
                    models.Product2BankAccount.product_id == 1,
                    models.Product2BankAccount.bank_account_id.not_in(
                        exclude.high_rule()
                    )
                )
            ).all()
        ]
    )


def calculate_external_loss(
    offset: datetime.timedelta | None = None
) -> typing.Tuple[
        list[typing.Tuple[int, int]],
        list[typing.Tuple[int, int]]
]:
    '''
    external loss is an amount of money that left the economy
    '''
    if offset is None:
        offset = datetime.timedelta(days=0)
    spent = [
        (
            transaction.seller_bank_account_id,
            transaction.count,
        )
        for transaction in 
        env.db.impl().session.query(
            models.Transaction
        ).filter(
            orm.and_(
                models.Transaction.product_id == 1,
                models.Transaction.customer_bank_account_id.in_(
                    exclude.high_rule()
                ),
                models.Transaction.seller_bank_account_id.not_in(
                    exclude.high_rule()
                ),
                models.Transaction.status == 'approved',
                (
                    orm.true 
                    if offset is not None else
                    models.Transaction.updated_at <= \
                        datetime.datetime.now() - offset
                )
            )
        ).all()
    ]

    consumed = [(
            account.id,
            np.sum(select_consumption_total(account.id, offset))
        )   
        for account in
        env.db.impl().session.query(
            models.BankAccount
        ).all()
    ]

    return np.asarray(spent), np.asarray(consumed)


def calculate_external_gain(
    offset: datetime.timedelta | None = None
) -> int:
    '''
    External gain is the amount of money transferred from outer source
    '''
    if offset is None:
        offset = datetime.timedelta(days=0)
    return np.asarray([
        (transaction.seller_bank_account_id, transaction.count) 
        for transaction in 
        env.db.impl().session.query(
            models.Transaction
        ).filter(
            orm.and_(
                models.Transaction.product_id == 1,
                models.Transaction.seller_bank_account_id.in_(
                    exclude.high_rule()
                ),
                models.Transaction.customer_bank_account_id.not_in(
                    exclude.high_rule()
                ),
                (
                    True == True
                    if offset is not None else
                    models.Transaction.updated_at <= \
                        datetime.datetime.now() - offset
                )
            )
        ).all()
    ])


def get_company_income(
    account: int,
    with_exact_timestamps: bool = False,
    exclude_government: bool = True,
    offset: datetime.timedelta | None = None
):
    transactions = env.db.impl().session.query(
        models.Transaction
    ).filter(
        orm.or_(
            models.Transaction.customer_bank_account_id == account,
            models.Transaction.seller_bank_account_id == account
        )
    ).filter(
        orm.and_(
            models.Transaction.status == 'approved',
            (
                True == True
                if not exclude_government else
                models.Transaction.customer_bank_account_id.not_in(
                    [int(id) for id in common.get_government()]
                )
            ),
            (
                True == True
                if offset is None else
                models.Transaction.updated_at >= datetime.datetime.now() - offset
            )
        )
    ).order_by(
        orm.asc(models.Transaction.updated_at)
    ).all()

    if not transactions:
        return [0], [0], [0]
    
    relative = np.min(
        [transaction.updated_at for transaction in transactions]
    )
    approximate_timestamp = lambda timestamp: \
        (timestamp - relative).total_seconds() / (60 * 60)
    
    
    approx, incomes, deltas, income = [], [], [], 0
    for transaction in transactions:
        delta = 0
        if transaction.product_id == 1:
            if transaction.customer_bank_account_id == account:
                income, delta = income + transaction.amount, delta + transaction.amount
            if transaction.seller_bank_account_id == account:
                income, delta = income - transaction.amount, delta - transaction.amount
        else:
            if transaction.seller_bank_account_id == account:
                income, delta = income + transaction.amount, delta + transaction.amount
            if transaction.customer_bank_account_id == account:
                income, delta = income - transaction.amount, delta - transaction.amount
        deltas.append(delta)
        approx.append(approximate_timestamp(transaction.updated_at))
        incomes.append(income)


    return approx, incomes, deltas


def plot_pie(data: list[typing.Tuple[int, int]], title: str) -> str:
    plt.figure(figsize=(6, 4))
    plt.title(title)

    total = np.sum([share for _, share in data])
    shares = np.asarray([
        np.sum([share for _, share in filtered]) / total 
        for filtered in (
            filter(lambda row: row[0] in common.get_users(), data),
            filter(lambda row: row[0] in common.get_companies(), data),
            filter(lambda row: row[0] in common.get_government(), data)
        )
    ]) * 100

    mask = shares > 0
    shares = shares[mask]
    labels = np.asarray(['пользователи', 'компании', 'госструктуры'])[mask]
    explode = np.ones(shares.shape[0]) * 0.1

    plt.pie(shares, explode=explode, labels=labels, autopct='%1.0f%%', shadow=True)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close("all")
    return base64.b64encode(buffer.getbuffer()).decode("ascii")


def plot_income(title: str, id: int | None = None) -> str:
    ids = [
        company.bank_account_id for company in env.db.impl().session.query(
            models.Company
        ).filter(
            models.Company.bank_account_id.not_in(exclude.high_rule())
        ).all()
    ]
    if id is not None:
        ids = [id]

    plt.figure(figsize=(6, 4))
    plt.title(title)
    plt.xlabel('Время, ч')
    plt.ylabel('Прибыль в надиках')
    
    for id in ids:
        x, y, _ = get_company_income(id)
        plt.plot(x, y)
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.grid(True)
    plt.close("all")
    return base64.b64encode(buffer.getbuffer()).decode("ascii")


@blueprints.stats.route('/view_statistics', methods=['GET'])
@flask_login.login_required
def view_statistics():
    share = calculate_total_market_share()
    spent, consumed = calculate_external_loss()
    gained = calculate_external_gain()
    
    summed_share, summed_spent, summed_gained = \
    (
        int(np.sum([share for _, share in share])),
        int(np.sum([share for _, share in spent])),
        int(np.sum([share for _, share in gained]))
    )

    spec = {
        'Общая сумма валюты в обороте': summed_share,
        'Общая сумма выведенной валюты': summed_spent,
        'Общая сумма введенной валюты': summed_gained
    }

    share_title, spent_title, gained_title = spec.keys()
    plotted_share, plotted_gain, plotted_spent = \
        plot_pie(share, share_title), \
        plot_pie(gained, gained_title), \
        plot_pie(spent, spent_title)

    companies = env.db.impl().session.query(
        models.Company
    ).filter(
        models.Company.bank_account_id.not_in(exclude.high_rule())
    ).all()

    companies = env.db.impl().session.query(
        models.Company
    ).filter(
        models.Company.bank_account_id.not_in(exclude.high_rule())
    ).all()

    return flask.render_template(
        'main/view_income.html',
        spec=spec,
        plotted_share=plotted_share,
        plotted_loss=plotted_spent,
        plotted_gain=plotted_gain,
        companies=companies
    )


@blueprints.stats.route('/view_company_statistics', methods=['GET'])
@flask_login.login_required
def view_company_statistics():
    company = flask.request.args.get('company', None)
    if company is None:
        return flask.abort(443, f'company is missing')
    
    company = int(company)
    obj = env.db.impl().session.query(
        models.Company
    ).filter(
        models.Company.bank_account_id == company
    ).first()

    income = plot_income(f'Доход компании {obj.name}', company)
    _, incomes, gains = get_company_income(company)
    _, shifted_incomes, shifted_gains = get_company_income(
        company, offset=datetime.timedelta(days=1, hours=12)
    )
    
    overall, shifted = incomes[-1], shifted_incomes[-1]

    gains, shifted_gains = np.asarray(gains), np.asarray(shifted_gains)
    positives_overall, positives_shifted = \
        np.sum(gains[gains > 0]), np.sum(shifted_gains[shifted_gains > 0])
    negatives_overall, negatives_shifted = \
        np.sum(gains[gains < 0]), np.sum(shifted_gains[shifted_gains < 0])

    company_spec = {
        'Общая прибыль за все время': overall,
        'Общий доход за все время': positives_overall,
        'Общие расходы за все время': negatives_overall,
        'Прибыль за последний день': shifted,
        'Доходы за последний день': positives_shifted,
        'Расходы за последний день': negatives_shifted
    }

    return flask.render_template(
        'main/view_company_income.html',
        plot=income,
        company_spec=company_spec
    )