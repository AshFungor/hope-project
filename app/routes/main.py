from flask import Blueprint, render_template
from flask_login import LoginManager

main = Blueprint('main', __name__)


login_manager = LoginManager()
login_manager.login_view = 'login.authorization'


@main.route('/')
@main.route('/index')

def index():
    return render_template('main/index.html')



