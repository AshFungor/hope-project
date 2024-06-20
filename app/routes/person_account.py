import flask
import flask_login

# local
import app.routes.blueprints as blueprints


@blueprints.accounts_blueprint.route('/person_account')
@flask_login.login_required
def person_account():
    current_user = flask_login.current_user
    specs = []

    mapper = {
        'bank_account_id': 'номер банковского счета',
        'login': 'логин',
        'birthday': 'день рождения'
    }

    for spec in ['bank_account_id', 'login', 'birthday']:
        specs.append({'name': mapper[spec], 'value': getattr(current_user, spec)})
    return flask.render_template('main/person_account_page.html', user_spec=specs)


