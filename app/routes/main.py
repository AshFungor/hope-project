from flask import Blueprint, render_template
from flask_login import LoginManager

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints

login_manager = LoginManager()
login_manager.login_view = 'login.authorization'


@blueprints.main.route('/')
@blueprints.main.route('/index')
def index():
    return render_template('main/index.html')