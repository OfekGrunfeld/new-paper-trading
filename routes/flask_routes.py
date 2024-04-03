from flask import current_app as flask_app
from flask import render_template, redirect
from flask.helpers import url_for
from requests import Response

from utils.render_readme import get_rendered_readme
from forms.userbase_logic import SignUpForm, LoginForm
from comms import get_sign_up_response
from utils import logger

@flask_app.route("/")
def index() -> str:
    return get_rendered_readme()
    

@flask_app.route("/login", methods=["GET", "POST"])
def login() -> str:
    form = LoginForm()
    if form.validate_on_submit(): # POST
        # communicate with fastAPI server to verify that the user is okay to log in to
        # Redirect to home page
        return redirect(url_for("index"))
    else: # GET
        return render_template("login.html", form=form)

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


@flask_app.route("/logout")
def logout():
    # logout_user()
    return redirect(url_for("index"))


@flask_app.route("/tradingview", methods=["GET", "POST"])
def tradingview_page() -> str:
    return render_template(
        "tradingview.html"
        )
