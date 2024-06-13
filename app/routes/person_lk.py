import datetime

import flask

from app.env import env

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints


@blueprints.accounts_blueprint.route('/person_lk')
def person_cabinet():
    return flask.render_template('main/person_lk_page.html')


