import datetime
import logging
import flask

from flask import Blueprint, redirect, request, render_template, url_for
from flask_login import login_required, current_user

from sqlalchemy import and_

from app import models
from app.env import env
from app.forms.transaction import TransactionForm
from app.modules.database.static import CurrentTimezone

transaction = Blueprint('transaction', __name__)


@transaction.route('/make_transaction', methods=['GET', 'POST'])
@login_required
def transaction_page():
    form = TransactionForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():  # validate form
            logging.info(f'user({current_user.id}) is trying to create a transaction')
            amount = form.amount.data
            customer_bank_account_id = form.bank_account.data

            # get seller Product2BankAccount and check your count
            customer_wallet = env.db.impl().session.query(models.Product2BankAccount).filter(and_(
                models.Product2BankAccount.bank_account_id == customer_bank_account_id,
                models.Product2BankAccount.product_id == 1,
            )).first()
            if customer_wallet:
                seller_wallet = env.db.impl().session.query(models.Product2BankAccount).filter(and_(
                    models.Product2BankAccount.bank_account_id == current_user.bank_account_id,
                    models.Product2BankAccount.product_id == 1,
                )).first()

                if seller_wallet.count < amount:
                    logging.info('transaction was not created')
                    flask.flash('У вас недостаточно денег', 'warning')
                    return redirect(url_for('transaction.transaction_page'))

                # making a transfer
                seller_wallet.count = seller_wallet.count - amount
                customer_wallet.count = customer_wallet.count + amount

                # approved transaction
                transaction = models.Transaction(
                    product_id=1,
                    customer_bank_account_id=customer_bank_account_id,
                    seller_bank_account_id=current_user.bank_account_id,
                    count=amount,
                    amount=amount,
                    status='approved',
                    updated_at=datetime.datetime.now(tz=CurrentTimezone),
                    comment=None,
                )
                env.db.impl().session.add(transaction)
                env.db.impl().session.commit()
                logging.info(f'user({current_user.id}) has created a transaction')
                flask.flash('Перевод успешно выполнен', 'info')
            else:
                logging.info('transaction was not created')
                flask.flash('Данного бансковского счета не существует', 'warning')
        else:
            logging.info('transaction was not created')
            flask.flash('Вы неверно заполнили форму', 'warning')
        return redirect(url_for('transaction.transaction_page'))
    return render_template('main/transaction.html', form=form)
