from requests import Response
from datetime import timedelta

from flask import current_app as flask_app
from flask import render_template, redirect, session
from flask.helpers import url_for

from utils.render_readme import get_rendered_readme 
from utils import logger, yfinance_helper
from forms.userbase_logic import SignUpForm, SignInForm
from forms.stocks_logic import SymbolPickForm, TradeForm, get_locked_trade_form
from comms import get_sign_up_response, get_sign_in_response, submit_order
from routes.utils.auth import sign_in_required, redirect_to_access_denied, _signed_in

@flask_app.before_request
def make_session_permanent():
    session.permanent = True
    flask_app.permanent_session_lifetime = timedelta(days=1)

    username = _signed_in()
    if not username:
        return

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
                    session["user_id"] = response_json["extra"]
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
@sign_in_required()
def sign_out():
    session.pop("username", None)
    session.pop("password", None)
    session.pop("user_id", None)

    return redirect(url_for("index"))

@flask_app.route('/my/dashboard')
@sign_in_required()
def profile_dashboard():
    return render_template(
        "profile_dashboard.html", 
        username=session["username"],
        user_id=session["user_id"]
        )

@flask_app.route('/stock_dashboard', methods=['GET'])
@flask_app.route('/stock_dashboard/', methods=['GET'])
@flask_app.route('/stock_dashboard/<symbol>', methods=['GET', 'POST'])
@sign_in_required()
def stock_dashboard(symbol: str = None):
    if symbol is None:
        return redirect_to_access_denied()
    
    symbol_form = SymbolPickForm()
    if symbol_form.validate_on_submit():
        # Handle symbol selection logic
        selected_symbol = symbol_form.symbol.data
        return redirect(f"{url_for(f'stock_dashboard')}/{selected_symbol}")
    
    symbol = symbol.upper()
    # got symbol
    info = yfinance_helper.get_symbol_info(symbol)
    try:
        print(f"Bid: {info["bid"]}, Ask: {info["ask"]}")
        # print(info)
    except:
        logger.error("symbol likely doesn't exist")
        info = None

    
    trade_form = TradeForm()
    if trade_form.validate_on_submit():
        logger.debug(f"Trade form submitted")
        logger.debug(f"Form data: {trade_form.data}")
        logger.debug(f"Submitting form to server")
        order = trade_form.data
        order["symbol"] = symbol
        response = submit_order(order)
        if isinstance(response, Response):
            print(response.status_code, response.json())
            try:
                response_json: dict = response.json()
                logger.debug("RIGHT PLACE")
                if response_json["success"] is True:
                    logger.debug("RIGHT PLACE2")
                    logger.info(f"Order {order} has been successful")
                    return redirect(f"{url_for(f'stock_dashboard')}/{symbol}")
                else:
                    logger.error(f"Order {order} has failed")
                    return redirect(f"{url_for(f'stock_dashboard')}/{symbol}")
            except Exception as error:
                logger.error(f"Got bad response from other server: {error}")
        if isinstance(response, dict):
            try:
                logger.debug(f"Communication between servers has failed: {response["internal_error"]}")
                return redirect(f"{url_for(f'stock_dashboard')}/{symbol}", error=response["internal_error"])
            except Exception as error:
                logger.error(f"Got bad response from own server: {error}")

        # Redirect or render template after processing
        return render_template(
            "stock_dashboard.html", 
            trade_form=TradeForm(formdata=None), 
            symbol_form=symbol_form,
            symbol=symbol
        )
    else:
        # Handle the GET request or form errors
        if info is not None:
            return render_template(
                "stock_dashboard.html", 
                trade_form=trade_form, 
                symbol_form=symbol_form,
                symbol=symbol,
                bid=info["bid"],
                ask=info["ask"]
            )
        else:
            return render_template(
                "stock_dashboard.html", 
                trade_form=get_locked_trade_form(), 
                symbol_form=symbol_form,
                symbol="Invalid symbol"
            )