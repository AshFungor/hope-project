import datetime
import logging

import flask
from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import login_required, current_user

from app import models
from app.forms.new_company import NewCompanyForm
from app.env import env
from app.modules.database.validators import CurrentTimezone


new_company = Blueprint('new_company', __name__)


def add_company(name: str, about: str, founders: tuple, prefecture_name: str) -> (bool, str):
    current_user_id = current_user.id
    prefecture_id = env.db.impl().session.query(models.Prefecture.id).filter_by(name=prefecture_name).first()[0]
    if not prefecture_id:
        logging.warning(f"user: {current_user_id} Create company failed: prefecture {prefecture_name} not found")
        return False, "Указанной префектуры не существует"
    bank_account = models.BankAccount(**models.BankAccount.make_spec('company', None))
    company = models.Company(
        bank_account_id=bank_account.id,
        prefecture_id=prefecture_id,
        name=name,
        about=about
    )
    ratio = 0
    founders_qty = len(founders)
    founders_id = []
    if founders_qty != len(set(founders)):
        logging.warning(f"user: {current_user_id} Create company failed: not unique founders")
        return False, "Указаны не уникальные учредители"
    for founder_bank_account in founders:
        founder_id = env.db.impl().session.query(models.User.id).filter_by(
            bank_account_id=founder_bank_account).first()
        if not founder_id:
            logging.warning(f"user: {current_user_id} Founder {founder_bank_account} not found during create company")
            return False, "Указанного учредителя не существует " + str(founder_bank_account)
        # пока все учредители имеют равные доли в компании (в идеале - не так)
        if ratio == 0:
            ratio = 100 - 100 // founders_qty * (founders_qty - 1)
        else:
            ratio = 100 // founders_qty
        founders_id.append((founder_id[0], ratio))
    try:
        env.db.impl().session.add(bank_account)
        env.db.impl().session.add(company)
        env.db.impl().session.commit()
    except Exception as error:
        logging.warning(f"user: {current_user_id} Create company failed.")
        return False, "Попытка создания компании не удалась"
    for founder_id, ratio in founders_id:
        user2company = models.User2Company(
            user_id=founder_id,
            company_id=company.id,
            role='founder',
            ratio=ratio,
            employed_at=datetime.datetime.now(tz=CurrentTimezone),
            fired_at=None
        )
        env.db.impl().session.add(user2company)
    env.db.impl().session.commit()
    return True, "Фирма успешно создана"


@new_company.route('/new_company', methods=['GET', 'POST'])
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
