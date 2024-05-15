from flask import Blueprint, render_template, url_for

admin_lk = Blueprint('admin_lk', __name__)


@admin_lk.route('/admin_lk')
def admin_cabinet():
    """Личный кабинет admin"""
    return render_template('main/admin_lk.html')
