import datetime

import flask

from app.env import env

import app.modules.database.static as static
import app.routes.blueprints as blueprints


@blueprints.accounts_blueprint.route('/prefecture_lk')
def prefecture_cabinet():
    return flask.render_template('main/prefecture_lk_page.html')
