from requests import Response

from flask import current_app as flask_app
from flask import render_template, redirect, session, request
from flask.helpers import url_for

from forms.userbase_logic import SignUpForm, SignInForm, UpdateUserForm
from comms.communications import get_sign_up_response, get_sign_in_response, get_user_database_table, get_update_user_response
from routes.utils.auth import sign_in_required
from utils.logger_script import logger

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
                if response_json["success"] is True:
                    session["uuid"] = response_json["data"]
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
                return url_for("sign_in", form=form, error=response["internal_error"])
            except Exception as error:
                logger.error(f"Got bad response from own server: {error}")
        
        # Redirect to home page
        return redirect(url_for("sign_in"))
    else:
        # somehow return that passwords don't match then redirect to the same page
        logger.error(f"User {form.username.data} log in has failed miserably")
        return render_template("users/sign_in.html", form=form)

@flask_app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    form = SignUpForm()

    if form.validate_on_submit() and form.password.data == form.repeat_password.data:
        # communicate with fastAPI server to regiter the user
        response = get_sign_up_response(email=form.email.data, username=form.username.data, password=form.password.data)
        
        if isinstance(response, Response):
            try:
                response_json: dict = response.json()
                logger.debug(f"Got response from fastAPI server: {response.status_code}, {response_json}")
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
        return render_template("users/sign_up.html", form=form,error=error)
    else:
        # somehow return that passwords don't match then redirect to the same page
        logger.error(f"User {form.username.data} sign up has failed miserably")
        return render_template("users/sign_up.html", form=form)

@flask_app.route('/sign_out')
@sign_in_required()
def sign_out():
    session.pop("username", None)
    session.pop("password", None)
    session.pop("uuid", None)

    return redirect(url_for("index"))

@flask_app.route('/my/dashboard')
@sign_in_required()
def profile_dashboard():
    return render_template(
        "users/profile_dashboard.html", 
        username=session["username"],
        uuid=session["uuid"]
    )

@flask_app.route('/my/data/<database_name>', methods=['GET'])
@sign_in_required()
def database_data(database_name: str):
    # add check to see if it's one of databases which are supported
    # add proper logic for redirecting and such
    response = get_user_database_table(database_name=database_name)

    if isinstance(response, Response):
        try:
            response_json: dict = response.json()
            if response_json["success"] is True:
                logger.info(f"Outputting transaction history to html...")
                return render_template(
                    "users/view_user_database_table.html", 
                    database_name=database_name.capitalize(),
                    username=session["username"],
                    records=response_json["data"]
                )
            else:
                logger.error(f"Failed getting user's transaction history")
                return redirect(f"{url_for('/my/dashboard')}")
        except Exception as error:
            logger.error(f"Got bad response from other server: {error}")
            return redirect(f"{url_for(f'profile_dashboard')}")

@flask_app.route('/update_user', methods=['GET', 'POST'])
def update_user():
    update_form = UpdateUserForm()

    if request.method == "POST" and update_form.validate_on_submit():
        logger.debug(f"Data is: {update_form.data}")

        if update_form.password.data != session["password"]:
            logger.warning(f"Password does not match session")
        else:
            attribute_to_update = update_form.attribute_to_update.data
            attribute_value = update_form.data[f"new_{attribute_to_update}"]

            response = get_update_user_response(attribute_to_update, attribute_value)

            if isinstance(response, Response):
                try:
                    response_json: dict = response.json()
                    logger.debug(f"Got response from fastAPI server: {response.status_code}, {response_json}")
                    if response_json["success"] == True:
                        logger.debug(f"User {session["username"]}'s update of {attribute_to_update} has been successful")
                        session[attribute_to_update] = attribute_value
                        logger.debug(f"User {attribute_to_update.capitalize()} is now {session[attribute_to_update]}")
                    else:
                        logger.error(f"User {session["username"]} update of {update_form.attribute_to_update.data} has failed")
                except Exception as error:
                    logger.error(f"Got bad response from other server: {error}")
            if isinstance(response, dict):
                try:
                    logger.debug(f"Communication between servers has failed: {response["internal_error"]}")
                except Exception as error:
                    logger.error(f"Got bad response from own server: {error}")
    else:
        logger.error(f"Update of user {session["username"]} failed")

    return render_template('users/update_user.html', update_form=UpdateUserForm())