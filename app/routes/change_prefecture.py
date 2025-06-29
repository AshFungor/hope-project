import logging

from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import login_required, current_user

import app.models as models
from app.forms.change_prefecture import SwitchPrefectureForm
from app.env import env

import app.routes.blueprints as blueprints


def switch_company_prefecture(company_bank_account: int, new_prefecture_name: str, user_id: int) -> tuple[bool, str]:
    session = env.db.impl().session

    company = session.query(models.Company).join(models.BankAccount).filter(
        models.BankAccount.id == company_bank_account
    ).first()

    if not company:
        logging.warning(f'user: {user_id}; Switch prefecture failed: company with account {company_bank_account} not found')
        return False, 'Фирма с таким счетом не найдена.'

    new_prefecture = session.query(models.Prefecture).filter_by(name=new_prefecture_name).first()
    if not new_prefecture:
        logging.warning(f'user: {user_id}; Switch prefecture failed: prefecture {new_prefecture_name} not found')
        return False, 'Указанная префектура не найдена.'

    company.prefecture_id = new_prefecture.id
    session.commit()

    logging.info(f'user: {user_id}; Switched company {company.id} to prefecture {new_prefecture_name}')
    return True, 'Префектура успешно изменена.'


@blueprints.master_blueprint.route('/switch_prefecture', methods=['GET', 'POST'])
@login_required
def switch_prefecture():
    """Смена префектуры фирмы"""
    form = SwitchPrefectureForm()
    form.set_choices_prefectures()

    if request.method == 'POST' and form.validate_on_submit():
        company_bank_account = form.company_bank_account.data
        new_prefecture_name = form.new_prefecture_name.data

        ok, message = switch_company_prefecture(company_bank_account, new_prefecture_name, current_user.id)

        if ok:
            flash(message, category='info')
            return redirect(url_for('master.switch_prefecture'))
        else:
            flash(message, category='warning')

    return render_template('main/change_prefecture.html', form=form)
