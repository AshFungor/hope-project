import logging
import flask

from flask import Blueprint, render_template, url_for, request, redirect
from flask_login import login_required, current_user

from sqlalchemy import and_

import app.models as models
from app.modules.database.static import StaticTablesHandler
from app.env import env

user_suggestions = Blueprint('user_suggestions', __name__)

@user_suggestions.route('/user_suggestions', methods=['GET', 'POST'])
@user_suggestions.route('/user_suggestions/<int:page>', methods=['GET', 'POST'])
def get_user_suggestions(page=1):

    #  try completed transaction
    if request.method == 'POST':
        logging.info(f'user_id: {current_user.id} request for transaction approval')
        status = 'rejected' if request.form.get('action') == 'Отклонить' else 'approved'
        completed, message = StaticTablesHandler.complete_transaction(request.form.get('transaction_id'), status)
        if completed:
            flask.flash(message)
            logging.info(f'user_id: {current_user.id} transaction({request.form.get("transaction_id")}) has been completed')
            env.db.impl().session.commit()
        else:
            logging.info('transaction was not completed')
            flask.flash(message)
        return redirect(url_for('user_suggestions.get_user_suggestions'))
    else:
        user_suggs = (
            env.db.impl().session.query(
                models.User.name,
                models.User.bank_account_id,
                models.Transaction.id,
                models.Transaction.amount,
                models.Transaction.count,
                models.Product.name.label('product_name')
                )
                .filter(and_(models.Transaction.status == 'created',
                             models.Transaction.customer_bank_account_id == current_user.bank_account_id))
                .join(models.User, models.User.bank_account_id == models.Transaction.seller_bank_account_id)
                .join(models.Product, models.Product.id == models.Transaction.product_id)
                .paginate(page=page, per_page=10, error_out=False)
        )
        logging.info(f'user_id: {current_user.id} requested your suggestions')
    return render_template('main/user_suggestions.html', user_suggestions=user_suggs)
