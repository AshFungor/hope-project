from flask import Blueprint, render_template, url_for, session
from flask_login import login_required

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints


@blueprints.accounts_blueprint.route('/city_hall_lk')
@login_required
def city_hall_cabinet():
    """Личный кабинет мэрии"""
    return render_template('main/city_hall.html', session=session)
