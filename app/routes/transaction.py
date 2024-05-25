from flask import Blueprint, redirect, request, render_template, url_for, session

import app.routes.transaction
from app.forms.transaction import TransactionForm

transaction = Blueprint('transaction', __name__)


@transaction.route('/transaction', methods=['GET', 'POST'])
def transaction_page():
    form = TransactionForm(request.form, meta={'csrf': False})
    if request.method == 'POST':
        if form.validate_on_submit():
            bank_account = form.bank_account.data
            amount = form.amount.data
            comment = form.comment.data
        else:
            pass
        return redirect(url_for('transaction.transaction_page'))
    return render_template('main/transaction.html', form=form, session=session)
