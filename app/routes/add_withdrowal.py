from flask import Blueprint, render_template, url_for
from flask_login import login_required

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints
import app.models as models


@blueprints.master_blueprint.route('/master_add_withdrowal')
@login_required
def master_add_withdrowal():
    return render_template('main/add_withdrowal.html', products=models.Product.get_all())