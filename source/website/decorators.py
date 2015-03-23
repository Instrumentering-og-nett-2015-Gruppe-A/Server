from functools import wraps
from flask_login import login_required, current_user
from flask import abort

def admin_required(func):

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.is_admin:
            return func(*args, **kwargs)
        abort(401)
    return login_required(decorated_view)