import sqlalchemy as orm

from flask import render_template
from flask_login import login_required

from app.routes import Blueprints
from app.models import City
from app.context import context, AppContext


@Blueprints.master.route("/master_create_office4company")
@login_required
@context
def master_add_office(ctx: AppContext):
    cities = ctx.database.session.scalars(orm.select(City)).all()
    return render_template("main/create_office.html", cities=cities)
