from flask import Blueprint, render_template, url_for
from flask_login import login_required

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints
@blueprints.accounts_blueprint.route('/company_lk')
@login_required
def company_cabinet():
    """Личный кабинет компании"""
    return render_template('main/company.html')