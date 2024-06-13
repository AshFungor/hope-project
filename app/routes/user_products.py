import flask_login
from flask import Blueprint, render_template
from flask_login import current_user, login_required

# database
import app.models as models
from app.env import env

user_products = Blueprint('user_products', __name__)


@user_products.route('/products')
@login_required
def get_user_products():
    products = env.db.impl().session.query(
        models.Product.name,
        models.Product.category,
        models.Product2BankAccount.count  # quantity of product
    ).filter(
        models.Product2BankAccount.bank_account_id == current_user.bank_account_id
    ).join(
        models.Product, models.Product2BankAccount.product_id == models.Product.id
    ).order_by(models.Product.category).all()

    categories = list(set(map(lambda x: x.category, products)))
    return render_template('main/user_products.html', products=products, categories=categories)
