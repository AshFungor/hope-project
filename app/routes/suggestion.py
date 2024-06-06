# base
import typing
import logging
import hashlib
import datetime

# flask
import flask
import flask_login

# local
from app.env import env
import app.models as models
import app.forms.suggestion as suggestion_form
import app.modules.database.validators as validators

from sqlalchemy import and_, or_

suggestion = flask.Blueprint('suggestion', __name__)


def query_request_data(product_name: str, id: str) -> None | typing.Tuple[models.Product2BankAccount, models.Product2BankAccount, models.Product, bytes]:
    request_id = int.from_bytes(hashlib.sha3_224((product_name + str(id)).encode('UTF-8') + str(datetime.datetime.now(validators.CurrentTimezone)).encode('UTF-8')).digest())
    logging.info(f'user: {flask_login.current_user.id} is trying to create a transaction: assigning id: {request_id}')

    product = env.db.impl().session.query(models.Product).filter_by(name=product_name).first()
    customer_bank_account = env.db.impl().session.get(models.BankAccount, id)

    customer_spec = env.db.impl().session.query(models.Product2BankAccount)                         \
        .filter(and_(
                models.Product2BankAccount.bank_account_id == flask_login.current_user.bank_account_id,
                or_(
                    models.Product2BankAccount.product_id == product.id if product else None,
                    models.Product2BankAccount.product_id == 1, # money?
                )
            )
        )                                                                                           \
    .order_by(models.Product2BankAccount.product_id).all()

    seller_wallet = seller_products = None
    try: 
        seller_wallet, seller_products = customer_spec
    except Exception as error:
        logging.warn(f'transaction: {request_id}; unpacking failed for products lookup')
        return

    env.db.impl().session.commit()
    if not customer_bank_account:
        logging.warn(f'transaction: {request_id}; customer bank account lookup failed for {id}')
    if not product:
        logging.warn(f'transaction: {request_id}; product lookup failed for {product_name}')
    
    if not (product and customer_bank_account):
        return
    
    return seller_wallet, seller_products, product, request_id


def add_proposal(
    id: bytes, 
    product : models.Product, 
    seller_wallet: models.Product2BankAccount, 
    seller_products: models.Product2BankAccount,
    count: int,
    amount: int,
    bank_account_id: int
) -> None | str:
    if seller_products.count < count:
        logging.warn(f'transaction: {id}; seller has less products that they can provide')
        return 'У вас недостаточно продуктов для данного предложения'
    elif seller_wallet.count < amount:
        logging.warn(f'transaction: {id}; seller has less money that they can provide')
        return 'У вас недостаточно надиков для данного предложения'

    transaction = models.Transaction(
        customer_bank_account_id=bank_account_id,
        product_id=product.id,
        seller_bank_account_id=flask_login.current_user.bank_account_id,
        count=count,
        amount=amount,
        status='created',
        updated_at=None,
        comment=None
    )
    env.db.impl().session.add(transaction)


@suggestion.route('/make_suggestion', methods=['GET', 'POST'])
@flask_login.login_required
def proposal():
    form = suggestion_form.SuggestionForm()
    if form.validate_on_submit() and flask.request.method == 'POST':
        logging.info(f'user: {flask_login.current_user.id} is trying to create a transaction')
        # get data
        customer_bank_account_id, product_name, count, amount = \
            form.bank_account.data, form.product.data, form.count.data, form.amount.data

        data = query_request_data(product_name, customer_bank_account_id)
        if not data:
            flask.flash(f'Мы не смогли создать предложение. Пожалуйста, проверьте правильность введенных данных', 'warning')
            return flask.render_template('main/suggestion.html', form=form)
        
        seller_wallet, seller_products, product, id = data
        result = add_proposal(id, product, seller_wallet, seller_products, count, amount, customer_bank_account_id)

        if isinstance(result, str):
            flask.flash(result, 'warning')
            return flask.render_template('main/suggestion.html', form=form)
        
        env.db.impl().session.commit()
        
    return flask.render_template('main/suggestion.html', form=form)
