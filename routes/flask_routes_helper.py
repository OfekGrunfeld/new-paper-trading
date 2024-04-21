from datetime import timedelta

from flask import current_app as flask_app
from flask import session
from routes.utils.auth import _signed_in

@flask_app.before_request
def make_session_permanent():
    session.permanent = True
    flask_app.permanent_session_lifetime = timedelta(days=1)

    username = _signed_in()
    if not username:
        return