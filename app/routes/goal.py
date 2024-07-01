import io
import base64
import typing
import datetime

import flask
import flask_login

import scipy.stats as stat
import sklearn.preprocessing as learn

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import sqlalchemy as orm

import app.models as models
import app.routes.blueprints as blueprints
import app.routes.person_account as accounts
import app.modules.statistics.excluders as exclude

from app.env import env

logger = env.logger.getChild(__name__)


def goal_picker(state: pd.DataFrame, **kwargs) -> pd.DataFrame:
    state.loc[state.shape[0]] = pd.Series(kwargs)
    return state


def get_goals(
        delta: datetime.timedelta, 
        offset: datetime.timedelta = datetime.timedelta()
) -> list[typing.Tuple[models.Goal, models.Product2BankAccount]]:
    now = datetime.datetime.now() - offset
    lower, upper = now - delta, now
    return env.db.impl().session.query(
        models.Goal,
        models.Product2BankAccount
    ).join(
        models.Product2BankAccount,
        models.Product2BankAccount.bank_account_id == models.Goal.bank_account_id
    ).filter(
        orm.and_(
            models.Goal.created_at < upper,
            models.Goal.created_at > lower,
            models.Product2BankAccount.product_id == 1,
            models.Goal.bank_account_id.not_in(exclude.high_rule())
        )
    ).order_by(
        models.Product2BankAccount.bank_account_id
    ).all()


def predict(diff: np.array) -> str:
    plt.figure(figsize=(6, 4))
    plt.title('Нормальное распределение абсолютных смещений')
    plt.ylabel('Оценка количества')
    plt.xlabel('Цель')
    bins = np.linspace(np.min(diff), np.max(diff), diff.shape[0])
    plt.plot(bins, stat.gaussian_kde(diff).evaluate(bins))
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    return base64.b64encode(buffer.getbuffer()).decode("ascii")


def account_goals(
        scale: bool = False,
        lower: float = 0.25,
        upper: float = 0.75,
        time_span: datetime.timedelta | None = None,
        time_offset: datetime.timedelta | None = None
) -> typing.Tuple[pd.DataFrame, np.array, int]:
    diffs, cached_queries = np.ones(0), np.ones(0)
    state = pd.DataFrame(
        columns=[
            'bank_account_id', 
            'value', 
            'diff', 
            'on_setup', 
            'on_validate', 
            'impact'
        ]
    )

    if time_span is None:
        time_span = datetime.timedelta(days=1)
    if time_offset is None:
        time_offset = datetime.timedelta(days=0)

    for goal, account in get_goals(time_span, time_offset):
        delta = account.count - goal.amount_on_setup
        goal.amount_on_validate = account.count
        if goal.value <= delta:
            # achieved
            goal.completed = True
        
        diff = -goal.value if goal.value > delta else goal.value
        diffs = np.append(diffs, diff)
        cached_queries = np.append(cached_queries,
            lambda impact, diff, goal=goal: goal_picker(state, 
                bank_account_id=goal.bank_account_id,
                diff=diff,
                on_setup=goal.amount_on_setup,
                on_validate=goal.amount_on_validate,
                impact=impact,
                value=goal.value
            )
        )

    if diffs.shape[0] == 0:
        return state, np.ones(0), 0

    mask = (
        np.quantile(diffs, lower) <= diffs
    ) & (
        diffs <= np.quantile(diffs, upper)
    )

    diffs, cached_queries = diffs[mask], cached_queries[mask]
    median, diffs = np.median(diffs), np.round(diffs, 4)

    if scale:
        diffs = learn.StandardScaler() \
            .fit_transform(diffs.reshape(-1, 1)) \
            .flatten()


    for query, diff in zip(cached_queries, diffs):
        state = query(
            round(
                (abs(diff) / np.sum(
                    diffs[diffs < 0 if diff < 0 else diffs > 0]
                )), 2),
            diff
        )
    
    env.db.impl().session.commit()
    return state, diffs, median


@blueprints.goal_model.route('/goal/make', methods=['POST'])
def create_goal():
    data = []
    for field in ['bank_account_id', 'value', 'amount_on_setup']:
        if field not in flask.request.form:
            return flask.abort(443, description=f'missing field: {field}')
        data.append(flask.request.form[field])
    account, target, current = data
    last = models.Goal.get_last(int(account), True)
    if last:
        return flask.abort(443, description=f'goal for today is already present')
    try:
        env.db.impl().session.add(models.Goal(account, target, current))
        env.db.impl().session.commit()
    except Exception as error:
        env.db.impl().session.rollback()
        error_message = 'Something went wrong during goal creation. Error: %s' % error
        logger.error(error_message)
        return flask.abort(400, description=error_message)
    return flask.redirect(flask.url_for('main.index'))


@blueprints.goal_view.route('/make_goal', methods=['GET'])
@flask_login.login_required
def view_create_goal():
    account = flask.request.args.get('account', None)
    if account is None:
        account = flask_login.current_user.bank_account_id

    return flask.render_template(
        'main/goal.html',
        bank_account_id=account,
        current=accounts.get_money(account)
    )


@blueprints.master_blueprint.route('/view_goals', methods=['GET'])
@flask_login.login_required
def view_goals():
    validate = flask.request.args.get('validate', 'OFF').upper().startswith('ON')

    if validate:
        # parse some args
        scale = flask.request.args.get('scale', 'OFF').upper().startswith('ON')
        lower = upper = span = offset = None
        try:
            lower = float(flask.request.args.get('lower', '0.25'))
            upper = float(flask.request.args.get('upper', '0.75'))
            span = datetime.timedelta(days=int(flask.request.args.get('span', '1')))
            offset = datetime.timedelta(days=int(flask.request.args.get('offset', '0')))
        except Exception as error:
            logger.warning('error on args parse while validating goals: %s' % error)
            return flask.abort(443, 'invalid args format')

        if not all(
            [0 <= quantile <= 1 for quantile in [lower, upper]] + 
            [lower < upper] +
            [0 <= delta.days <= 14 for delta in [span, offset]]
        ):
            return flask.abort(443, 'invalid args values')
        
        logger.info(
            f'validating goals with quintiles {lower} and {upper}; '
            f'time span = {span} and offset = {offset}'
        )

        stats, diff, median = account_goals(scale, lower, upper, span, offset)

        if not diff.shape[0]:
            return flask.abort(400, 'batch is empty')

        plot = predict(diff)
        shift = round(np.sum(diff), 10) * (median if scale else 1)

        spec = {
            'медиана': median,
            'нижний квантиль': lower,
            'верхний квантиль': upper,
            'абсолютное смещение (итоговое значение валидации)': shift
        }

        return flask.render_template(
            'main/view_goals.html', 
            stats=stats, 
            shift=shift, 
            size=stats.shape[0], 
            plot=plot,
            spec=spec
        )

    data = [
        (goal, account, models.Goal.get_rate(goal, accounts.get_money(account.bank_account_id))) 
        for goal, account in get_goals(datetime.timedelta(days=1))
    ]
    return flask.render_template('main/view_goals.html', data=data, size=len(data))

