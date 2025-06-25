import sqlalchemy as orm

from flask import render_template
from flask_login import login_required

from app.routes import Blueprints
from app.models import City
from app.context import function_context, AppContext


@Blueprints.master.route("/master/create/office4company")
@login_required
@function_context
def master_add_office(ctx: AppContext):
    cities = ctx.database.session.scalars(orm.select(City)).all()
    return render_template("accounts/master/create_office.html", cities=cities)
