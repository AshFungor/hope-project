from flask import Blueprint, render_template, url_for
from flask_login import login_required

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints
import app.models as models


@blueprints.master_blueprint.route('/master_create_office4company')
@login_required
def master_add_office():
    return render_template('main/create_office.html', cities=models.City.get_all())