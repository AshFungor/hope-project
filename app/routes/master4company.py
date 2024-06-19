from flask import Blueprint, render_template, url_for
from flask_login import login_required

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints


@blueprints.master_blueprint.route('/master_company')
@login_required
def master_company():
    """Мастер что-то делает с фирмой"""
    return render_template('main/master4company.html')