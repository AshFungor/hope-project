from flask import render_template
from flask_login import login_required

from app.routes import Blueprints


@Blueprints.accounts.route("/admin")
@login_required
def admin():
    return render_template("main/admin.html")
