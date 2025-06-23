from flask import Blueprint, render_template, url_for
from flask_login import login_required

import app.models as models

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints


@blueprints.master_blueprint.route("/master_add_withdrawal")
@login_required
def master_add_withdrowal():
    return render_template("main/add_withdrawal.html", products=models.Product.get_all())
