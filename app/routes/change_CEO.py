from datetime import datetime
import pytz
import flask
import sqlalchemy

from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import login_required

import app.models as models
from app.env import env
from app.forms.change_ceo import ChangeCeoForm

import app.routes.blueprints as blueprints


@blueprints.master_blueprint.route('/change_ceo_view', methods=['GET', 'POST'])
@login_required
def change_ceo_view():
    form = ChangeCeoForm()

    if request.method == 'POST' and form.validate_on_submit():
        company_account_id = form.company_id.data
        new_ceo_bank_account_id = form.new_ceo_id.data

        session = env.db.impl().session()

        company = session.execute(
            sqlalchemy.select(models.Company).filter(
                models.Company.bank_account_id == company_account_id
            )
        ).scalar_one_or_none()

        if company is None:
            flash('Компания не найдена', category='warning')
            return render_template('main/ceo_change.html', form=form)

        real_company_id = company.id

        new_ceo = session.execute(
            sqlalchemy.select(models.User).filter(
                models.User.bank_account_id == new_ceo_bank_account_id
            )
        ).scalar_one_or_none()

        if new_ceo is None:
            flash('Пользователь (новый генеральный директор) не найден', category='warning')
            return render_template('main/ceo_change.html', form=form)

        old_ceo = session.execute(
            sqlalchemy.select(models.User2Company).filter_by(
                company_id=real_company_id,
                role='CEO'
            )
        ).scalar_one_or_none()

        new_ceo_link = session.execute(
            sqlalchemy.select(models.User2Company).filter_by(
                company_id=real_company_id,
                user_id=new_ceo.id
            )
        ).scalar_one_or_none()

        if new_ceo_link is None:
            new_ceo_link = models.User2Company(
                user_id=new_ceo.id,
                company_id=real_company_id,
                role='CEO',
                ratio=0,
                employed_at=datetime.now(pytz.timezone('Europe/Moscow'))
            )
            session.add(new_ceo_link)
        else:
            new_ceo_link.role = 'CEO'

        if old_ceo and old_ceo.user_id != new_ceo.id:
            session.delete(old_ceo)

        try:
            session.commit()
            flash('Генеральный директор успешно обновлён', category='info')
            return redirect(url_for('master.change_ceo_view'))
        except Exception as ex:
            session.rollback()
            flash(f'Ошибка при обновлении CEO: {ex}', category='warning')

    return render_template('main/ceo_change.html', form=form)
