from flask import Blueprint, render_template, url_for
from flask_login import login_required

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints


@blueprints.master_blueprint.route('/master_city_hall')
@login_required
def master_city_hall():
    """Мастер что-то делает с мэрией"""
    return render_template('main/master4city_hall.html')