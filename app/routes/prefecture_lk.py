from flask import abort, render_template
from flask_login import current_user, login_required

import app.routes.blueprints as blueprints
from app.env import env
from app.models import Goal
from app.models.helpers import get_bank_account_size, get_goal_on_current_day

logger = env.logger.getChild(__name__)


@blueprints.accounts_blueprint.route('/prefecture_lk')
@login_required
def prefecture_cabinet():
    """Личный кабинет префектуры"""
    loginned_user_id = current_user.id
    prefecture = current_user.city.prefecture
    if not prefecture:
        logger.error(
            'There is no prefecture associated with the user: %s', loginned_user_id
        )
        return abort(
            400,
            description='There is no prefecture associated with the user: %s'
            % loginned_user_id,
        )
    prefecture_current_account_size = get_bank_account_size(prefecture.bank_account_id)
    if prefecture_current_account_size is None:
        logger.error(
            'Something went wrong. Can not find size of prefecture bank account: %s',
            prefecture.bank_account_id,
        )
        return abort(
            400,
            description='Something went wrong. Can not find size of prefecture bank account: %s'
            % prefecture.bank_account_id,
        )
    prefecture_goal = get_goal_on_current_day(prefecture.bank_account_id)
    goal_win_rate = None
    if prefecture_goal:
        goal_win_rate = _calculate_goal_winrate(
            prefecture_current_account_size, prefecture_goal
        )
    return render_template(
        'main/prefecture_lk_page.html',
        user=current_user,
        prefecture=prefecture,
        prefecture_goal=prefecture_goal,
        prefecture_current_account_size=prefecture_current_account_size,
        goal_win_rate=goal_win_rate,
    )


def _calculate_goal_winrate(ba_size: int, goal: Goal) -> int:
    win_rate = int(100 * (ba_size - goal.amount_on_setup) / goal.value)
    return win_rate
