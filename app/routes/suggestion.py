import logging

import flask
from flask import Blueprint, redirect, request, render_template, url_for, session
from flask_login import current_user
from app.forms.suggestion import SuggestionForm

from sqlalchemy import and_, or_

from app.env import env
import app.models as models

suggestion = Blueprint('suggestion', __name__)


@suggestion.route('/make_suggestion', methods=['GET', 'POST'])
def sug():
    form = SuggestionForm()
    if form.validate_on_submit() and request.method == 'POST':
        logging.info(f'user: {current_user.id} is trying to create a transaction')
        # get data
        customer_bank_account_id = form.bank_account.data
        product_name = form.product.data
        count = form.count.data
        amount = form.amount.data

        product = env.db.impl().session.query(models.Product).filter_by(name=product_name).first()
        customer_bank_account = env.db.impl().session.get(models.BankAccount, customer_bank_account_id)
        seller_wallet_products = env.db.impl().session.query(models.Product2BankAccount).filter(and_(
            models.Product2BankAccount.bank_account_id == current_user.bank_account_id,
            or_(
                models.Product2BankAccount.product_id == product.id if product else None,
                models.Product2BankAccount.product_id == 1,
            )
        )).order_by(models.Product2BankAccount.product_id).all()
        expected_num_of_rows = 2

        # check it
        if product and \
           customer_bank_account and \
           (customer_bank_account_id != current_user.bank_account_id) and \
           len(seller_wallet_products) == expected_num_of_rows:
            seller_wallet, seller_products = seller_wallet_products
            if seller_products.count < count:
                flask.flash('У вас недостаточно продуктов для данного предложения', 'warning')
                logging.info('transaction was not created')
            elif seller_wallet.count < amount:
                logging.info('transaction was not created')
                flask.flash('У вас недостаточно надиков для данного предложения', 'warning')
            else:
                transaction = models.Transaction(
                    customer_bank_account_id=customer_bank_account_id,
                    product_id=product.id,
                    seller_bank_account_id=current_user.bank_account_id,
                    count=count,
                    amount=amount,
                    status='created',
                    updated_at=None,
                    comment=None
                )
                env.db.impl().session.add(transaction)
                env.db.impl().session.commit()
                flask.flash('Предложение было успешно создано',
                            'info')
        else:
            logging.info('transaction was not created')
            flask.flash('Мы не смогли создать предложение. Пожалуйста, проверьте правильность введенных данных',
                        'warning')
    return render_template('main/suggestion.html', form=form)
