from flask import Blueprint, render_template, url_for
from flask_login import login_required

admin_lk = Blueprint('admin_lk', __name__)


@admin_lk.route('/admin_lk')
@login_required
def admin_cabinet():
    """Личный кабинет admin"""
    return render_template('main/admin_lk.html')
