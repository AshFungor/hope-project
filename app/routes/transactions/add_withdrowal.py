from flask import render_template
from flask_login import login_required

from app.routes import Blueprints
from app.routes.queries.common.products import get_all_products


@Blueprints.master.route("/master_add_withdrawal")
@login_required
def master_add_withdrawal():
    return render_template("main/add_withdrawal.html", products=get_all_products())
