from flask import Blueprint, redirect, request, render_template, url_for
from flask_login import login_required

from app.forms.goal_select import GoalForm

goal_select = Blueprint('goal_select', __name__)


@goal_select.route('/goal_select', methods=['GET', 'POST'])
@login_required
def select_goal_page():
    """Постановка цели"""
    form = GoalForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            return redirect(url_for('main.index'))
    return render_template('main/select_goal.html', form=form)
