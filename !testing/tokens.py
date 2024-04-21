from utils import ItsdangerousSession, ItsdangerousSessionInterface

"""
in the flask app:
"""
# for interpreter
from datetime import timedelta
from flask import Flask, url_for, redirect
from typing import Callable

flask_app: Flask= None
session: ItsdangerousSession = None


flask_app.session_interface = ItsdangerousSessionInterface() 
flask_app.secret_key = ';\xdb\xb2\xcc'


@flask_app.before_request
def make_session_permanent():
    session.permanent = True
    flask_app.permanent_session_lifetime = timedelta(days=1)

    username = logged_in()
    if not username:
        return

def login():
    """
    Example to show how cookies are handled by Flask
    """
    forms = None
    session["username"] = forms.username.data

def logged_in():
    if 'username' in session:
        # cookie already created, and decoded...
        return session['username']
    else:
        # user not logged in
        return None

def check_logged_in():
    def wrapper(func: Callable):
        import functools
        @functools.wraps(func)
        def f(*args, **kwargs):
            # first check for logged in
            username = logged_in()
            if not username:
                return redirect(url_for("login"))
            return func(*args, **kwargs)
        return f
    return wrapper

@flask_app.route('/logout')
@check_logged_in()
def logout():
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for("login"))