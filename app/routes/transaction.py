import datetime
import logging
import flask

from flask import Blueprint, redirect, request, render_template, url_for
from flask_login import login_required, current_user

from sqlalchemy import and_

from app import models
from app.env import env
from app.forms.transaction import TransactionForm
from app.modules.database.static import CurrentTimezone

import app.routes.blueprints as blueprints

@blueprints.accounts_blueprint.route('/transactiona')
@login_required
def transactiona():
    
    return render_template('main/transaction.html')


@blueprints.accounts_blueprint.route('/transactiona_view')
@login_required
def transactiona_view():
    
    return render_template('main/transaction_view.html')
