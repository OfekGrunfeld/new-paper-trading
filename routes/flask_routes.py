from requests import Response
from datetime import timedelta
from typing import Callable
from functools import wraps

from flask import current_app as flask_app
from flask import render_template, redirect, session, request
from flask.helpers import url_for

from utils.render_readme import get_rendered_readme 
from utils import logger
from forms.userbase_logic import SignUpForm, SignInForm
from forms.stocks_logic import SymbolPickForm
from comms import get_sign_up_response, get_sign_in_response



@flask_app.before_request
def make_session_permanent():
    session.permanent = True
    flask_app.permanent_session_lifetime = timedelta(days=1)

    username = _signed_in()
    if not username:
        return

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

def check_signed_in():
    """
    Decorator to check if a user is signed in 
    """
    def wrapper(func: Callable):
        @wraps(func)
        def f(*args, **kwargs):
            # first check for logged in
            username = _signed_in()
            requested_page: str = url_for(request.endpoint, **request.view_args).lstrip(r'/')
            if not username:
                print("right place")
                return render_template("access_denied.html", requested_page=requested_page)
            return func(*args, **kwargs)
        return f
    return wrapper

@flask_app.route("/")
def index() -> str:
    return get_rendered_readme()
    
    
@flask_app.route("/sign_in", methods=["GET", "POST"])
def sign_in() -> str:
    form = SignInForm()

    if form.validate_on_submit():
        # communicate with fastAPI server to regiter the user
        print(f"{form.data}")
        response = get_sign_in_response(username=form.username.data, password=form.password.data)
        if isinstance(response, Response):
            print(response.status_code, response.json())
            try:
                response_json: dict = response.json()
                logger.debug("RIGHT PLACE")
                if response_json["success"] is True:
                    logger.debug("RIGHT PLACE2")
                    session["username"] = form.username.data
                    session["password"] = form.password.data
                    logger.debug(f"User {form.username.data} log in has been successful")
                    return redirect(url_for("index"))
                else:
                    logger.error(f"User {form.username.data} log in has failed")
                    return redirect(url_for("sign_in", form=form, error=response_json["error"]))
            except Exception as error:
                logger.error(f"Got bad response from other server: {error}")
        if isinstance(response, dict):
            try:
                logger.debug(f"Communication between servers has failed: {response["internal_error"]}")
                return redirect(url_for("sign_in", form=form, error=response["internal_error"]))
            except Exception as error:
                logger.error(f"Got bad response from own server: {error}")
        
        # Redirect to home page
        return redirect(url_for("sign_in"))
    else:
        # somehow return that passwords don't match then redirect to the same page
        logger.error(f"User {form.username.data} log in has failed miserably")
        return render_template("sign_in.html", form=form)

@flask_app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    form = SignUpForm()

    if form.validate_on_submit() and form.password.data == form.repeat_password.data:
        # communicate with fastAPI server to regiter the user
        print(f"{form.data}")
        response = get_sign_up_response(email=form.email.data, username=form.username.data, password=form.password.data)
        
        if isinstance(response, Response):
            try:
                response_json: dict = response.json()
                if response["success"] == True:
                    logger.debug(f"User {form.username.data} sign up has been successful")
                else:
                    logger.error(f"User {form.username.data} sign up has failed")
            except Exception as error:
                logger.error(f"Got bad response from other server: {error}")
        if isinstance(response, dict):
            try:
                logger.debug(f"Communication between servers has failed: {response["internal_error"]}")
            except Exception as error:
                logger.error(f"Got bad response from own server: {error}")
        
        # Redirect to home page
        return redirect(url_for("index"))
    elif form.validate_on_submit() and form.password.data != form.repeat_password.data:
        error = "Passwords do not match"
        return render_template("sign_up.html", form=form,error=error)
    else:
        # somehow return that passwords don't match then redirect to the same page
        logger.error(f"User {form.username.data} sign up has failed miserably")
        return render_template("sign_up.html", form=form)

@flask_app.route('/sign_out')
@check_signed_in()
def sign_out():
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for("index"))

@flask_app.route('/stock_dashboard', methods=['GET', 'POST'])
@check_signed_in()
def stock_dashboard(symbol: str = None):    
    form = SymbolPickForm()

    
    if form.validate_on_submit():
        print("right place")
        print(f"Stock got: {form.symbol.data}")
        return render_template('stock_dashboard.html', form=form, symbol=form.symbol.data)
    else:
        return render_template('stock_dashboard.html', form=form)
