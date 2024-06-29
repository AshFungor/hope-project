from flask import Blueprint, render_template, url_for, session
from flask_login import login_required, current_user

# local
import app.modules.database.static as static
import app.routes.blueprints as blueprints

from app.env import env
import app.models as models

import sqlalchemy

from app.routes.person_account import get_money

@blueprints.accounts_blueprint.route('/city_hall_lk')
@login_required
def city_hall_cabinet():

    loginned_user_id = current_user.id

    info = sqlalchemy.select(
            models.CityHall
    )
    data = env.db.impl().session.execute(info).scalars().first()
    bank_account = data.bank_account_id
    mayor_id = data.mayor_id
    economic_assistant_id = data.economic_assistant_id
    social_assistant_id = data.social_assistant_id

    names = sqlalchemy.select(
        models.User
    ).filter(models.User.id.in_((mayor_id, economic_assistant_id, social_assistant_id)))
    data = env.db.impl().session.execute(names).scalars().all()
    spec = {name.id: name.full_name_string for name in data}

    mayor = spec[mayor_id]
    economic_assistant = spec[economic_assistant_id]
    social_assistant = spec[social_assistant_id]

    role = False
    if loginned_user_id in (mayor_id, economic_assistant_id, social_assistant_id):
        role = True

    return render_template('main/city_hall.html', 
                            session=session,
                            balance=get_money(bank_account),
                            bank_account=bank_account,
                            mayor=mayor,
                            economic_assistant=economic_assistant,
                            social_assistant=social_assistant,
                            role=role
                            )
