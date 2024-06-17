import flask
from flask import Blueprint, render_template, url_for, request
from flask_login import login_required, current_user

import sqlalchemy

from app.env import env
import app.models as models

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints
from app.models.helpers import get_bank_account_size


@blueprints.accounts_blueprint.route('/person_account')
@login_required
def person_account():
    query_user = sqlalchemy.select(models.User).filter(models.User.id == current_user.id)
    user = env.db.impl().session.execute(query_user).first()[0]
    balance = get_bank_account_size(user.bank_account_id)
    return render_template('main/person_account_page.html', user=user, balance=balance)
