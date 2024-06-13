import typing
import logging
import datetime

import flask
import flask_login

import numpy as np

from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import login_required, current_user

import app.models as models
from app.forms.new_company import NewCompanyForm
from app.env import env

from app.modules.database.validators import CurrentTimezone
import app.routes.blueprints as blueprints
import app.modules.database.static as static


def make_company(name: str, about: str, prefecture_name: str, user_id: int) -> models.Company | None:
    prefecture_id = env.db.impl().session.query(models.Prefecture).filter_by(name=prefecture_name).first()
    if not prefecture_id:
        logging.warning(f'user: {user_id}; Create company failed: prefecture {prefecture_name} not found')
        return
    
    bank_account = static.StaticTablesHandler.prepare_bank_account(**models.BankAccount.make_spec('company', {
        'name': name, 'about': about, 'prefecture_name': prefecture_name
    }))

    try:
        return models.Company(
            bank_account,
            prefecture_id,
            name,
            about
        )
    except ValueError as value_error:
        logging.warning(f'company params validation failed: {value_error}')
        return


def add_company(name: str, about: str, founders: list[int], prefecture_name: str) -> typing.Tuple[bool, str]:
    current_user_id = flask_login.current_user.id
    
    company = make_company(name, about, prefecture_name, current_user)

    if np.unique(founders).shape[0] != len(founders):
        logging.warning(f'user: {current_user_id} Create company failed: not unique founders')
        return False, 'Указаны не уникальные учредители'

    ids = env.db.impl().session.query(models.User).filter_by(
        models.User.bank_account_id in founders
    ).all()
    if len(ids) < len(founders):
        logging.warning(f'user: {current_user_id} Failed to match user ids against database records')
        return False, 'Указанного учредителя не существует '

    ratios = np.ceil(np.ones(len(founders)) * (1 / len(founders)) * 100)
    ratios[-1] += 100 - np.sum(ratios)
    
    for founder, ratio in zip(ids, ratios):
        env.db.impl().session.add(models.User2Company(
            founder,
            company.id,
            'founder',
            ratio,
            None,
            datetime.datetime.now(tz=CurrentTimezone)
        ))
    
    env.db.impl().session.add(company)
    env.db.impl().session.commit()

    return True, "Фирма успешно создана"


@blueprints.accounts_blueprint.route('/new_company', methods=['GET', 'POST'])
@login_required
def create_company():
    """Создание новой фирмы"""
    form = NewCompanyForm()
    form.set_choices_prefectures()

    if request.method == 'POST' and form.validate_on_submit():
        name = form.company_name.data
        description = form.about.data
        founders = tuple(map(int, form.founders.data.strip().split()))  # founders - это список расчётных счетов учредителей фирмы
        prefecture_name = form.prefecture.data
        created, message = add_company(name, description, founders, prefecture_name)

        if created:
            flask.flash(message, category="info")
            return redirect(url_for("new_company.create_company"))
        else:
            flask.flash(message, category="warning")
    return render_template('main/new_company.html', form=form)
