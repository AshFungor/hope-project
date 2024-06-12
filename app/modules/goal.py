from functools import wraps
from flask import request, redirect, url_for, g
from flask_login import current_user


def goal_required(func):
    """Декоратор для перенаправления на страницу выбора цели, при ее отсутствии
    :param func: функция-роут для декорирования
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        # current_user
        if True:
            return redirect(url_for('select_goal_page', value=current_user))
        else:
            return func(*args, **kwargs)

    return decorated_view
