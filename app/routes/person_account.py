import flask

# local
import app.routes.blueprints as blueprints


@blueprints.accounts_blueprint.route('/person_account')
def person_account():
    return flask.render_template('main/person_account_page.html')


