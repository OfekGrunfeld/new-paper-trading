from typing import Callable, Union, Any
from functools import wraps

from flask import render_template, session, url_for, request, redirect

from utils.logger_script import logger

def get_current_page() -> Union[Any, str, None]:
    try:
        requested_page: str = url_for(request.endpoint, **request.view_args).lstrip(r'/')
        return requested_page
    except Exception as error:
        logger.error(f"Could not get current page: {error}")
        return None

def _signed_in():
    """
    Internal function to check if a user 
    is signed in through the session
    """
    if 'username' in session:
        # cookie already created, and decoded...
        return session['username']
    else:
        # user not logged in
        return None

def sign_in_required():
    """
    Decorator to check if a user is signed in 
    """
    def wrapper(func: Callable):
        @wraps(func)
        def f(*args, **kwargs):
            # first check for logged in
            username = _signed_in()
            if not username:
                return render_template("misc/access_denied.html", requested_page=get_current_page(), reason="To view this page you must be logged in")
            return func(*args, **kwargs)
        return f
    return wrapper

def redirect_to_access_denied(reason: str = None):
    try:
        return render_template("misc/access_denied.html", requested_page=get_current_page(), reason=reason)
    except Exception as error:
        logger.error(f"Could not redirect to denied access page. redirected to home page")
        return redirect(url_for("index"))