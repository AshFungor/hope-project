from flask import Blueprint, render_template, url_for
from flask_login import login_required

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints


@blueprints.accounts_blueprint.route("/admin_lk")
@login_required
def admin_cabinet():
    """Личный кабинет admin"""
    return render_template("main/admin_lk.html")
