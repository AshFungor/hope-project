from flask import Blueprint, render_template, url_for, session


main = Blueprint('main', __name__)


@main.route('/')
@main.route('/index')
def index():

    return render_template('main/index.html', session=session)
