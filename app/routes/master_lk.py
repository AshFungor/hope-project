from flask import Blueprint, render_template, url_for
from flask_login import login_required

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints


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