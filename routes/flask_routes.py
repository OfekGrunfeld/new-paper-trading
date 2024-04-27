from datetime import timedelta
from requests import Response
from typing import List, Dict, Union
from collections import defaultdict

from requests import Response

from flask import current_app as flask_app
from flask import render_template, redirect, session, request
from flask.helpers import url_for

# Modules
from utils.render_readme import get_rendered_readme 
from utils.logger_script import logger
from utils.yfinance_helper import get_current_prices_of_symbol_list, get_symbol_info

from forms.userbase_logic import SignUpForm, SignInForm, UpdateUserForm
from forms.stocks_logic import SymbolPickForm, TradeForm, get_locked_trade_form

from comms.communications import get_response, FastAPIRoutes

from routes.utils.auth import _signed_in, sign_in_required, redirect_to_access_denied
from routes.dash_routes import shares_graph, worths_graph

class InternalError(Exception):
    pass

@flask_app.before_request
def make_session_permanent():
    session.permanent = True
    flask_app.permanent_session_lifetime = timedelta(days=1)

    username = _signed_in()
    if not username:
        return

@flask_app.route("/", methods=["GET"])
def index() -> str:
    return render_template(
        "index.html"
    )

@flask_app.route("/readme", methods=["GET"])
def readme() -> str:
    return get_rendered_readme()

@flask_app.route('/stock_dashboard/', methods=['GET', 'POST'])    
@flask_app.route('/stock_dashboard/<symbol>', methods=['GET', 'POST'])
@sign_in_required()
def stock_dashboard(symbol: str = None):
    if symbol is None:
        return redirect(f"{url_for('stock_dashboard')}/aapl")
    
    symbol_form = SymbolPickForm()
    if symbol_form.validate_on_submit():
        # Handle symbol selection logic
        selected_symbol = symbol_form.symbol.data
        return redirect(f"{url_for(f'stock_dashboard')}/{selected_symbol}")
    
    symbol = symbol.upper()
    # got symbol
    info = get_symbol_info(symbol)
    try:
        print(f"Bid: {info["bid"]}, Ask: {info["ask"]}")
        # print(info)
    except:
        logger.error("symbol likely doesn't exist")
        info = None

    # Tradeform part
    trade_form = TradeForm()
    if trade_form.validate_on_submit():
        logger.debug(f"Trade form submitted")

        logger.debug(f"Submitting form to server")
        order = trade_form.data
        order["symbol"] = symbol
        response = get_response(endpoint=FastAPIRoutes.submit_order.value, method="post", data_to_send={"order": order})
        try:
            if "internal_error" in response.keys():
                raise InternalError
            if response["success"] is True:
                logger.info(f"Order {order} has been successful")
                return redirect(f"{url_for(f'stock_dashboard')}/{symbol}")
            else:
                logger.error(f"Order {order} has failed")
                return redirect(f"{url_for(f'stock_dashboard')}/{symbol}")
        except InternalError:
            logger.debug(f"Communication between servers has failed: {response["internal_error"]}")
            return redirect(f"{url_for(f'stock_dashboard')}/{symbol}", error=response["internal_error"])
        except Exception as error:
            logger.error(f"Error: {error}")

        # Redirect or render template after processing
        return render_template(
            "stocks/stock_dashboard.html", 
            trade_form=TradeForm(formdata=None), 
            symbol_form=symbol_form,
            symbol=symbol
        )
    else:
        # Handle the GET request or form errors
        if info is not None:
            return render_template(
                "stocks/stock_dashboard.html", 
                trade_form=trade_form, 
                symbol_form=symbol_form,
                symbol=symbol,
                bid=info["bid"],
                ask=info["ask"]
            )
        else:
            return render_template(
                "stocks/stock_dashboard.html", 
                trade_form=get_locked_trade_form(), 
                symbol_form=symbol_form,
                symbol="Invalid symbol"
            )

@flask_app.route('/my/portfolio', methods=['GET'])            
@flask_app.route('/my/portfolio/', methods=['GET'])      
@flask_app.route('/my/portfolio/<symbol>', methods=['GET'])    
@sign_in_required()
def portfolio(symbol: str = None):
    if symbol is not None:
        symbol = symbol.upper()
    response = get_response(endpoint=FastAPIRoutes.get_portfolio.value, method="get")
    try:
        if "internal_error" in response.keys():
            raise InternalError
        if response["success"]:
            current_prices = get_current_prices_of_symbol_list(response["data"]["symbols"].keys())
            if symbol is None:
                symbols: dict[str, list[dict[str, Union[str, float]]]]= response["data"]["symbols"]           

                # Calculate the total shares for each symbol      
                # key = symbol   
                total_shares: dict[str, float] = defaultdict(float)
                for key_symbol, transactions in symbols.items():
                    for transaction in transactions:
                        total_shares[key_symbol] += transaction["shares"]
                
                # Calculate the total worth for each symbol
                total_worths: dict[str, float] = {}
                for key_symbol, shares in total_shares.items():
                    total_worths[key_symbol] = shares * current_prices[key_symbol]
                
                # Create pie charts for use in jinja template
                shares_graph.change_page_layout(total_shares)
                worths_graph.change_page_layout(total_worths)

                return render_template(
                    "users/portfolio.html",
                    balance=response["data"]["balance"],
                    symbols=response["data"]["symbols"],
                    total_shares=total_shares,
                    total_worths=total_worths
                )
            elif symbol in response["data"]["symbols"]:
                return render_template(
                    "users/stock.html",
                    balance=response["data"]["balance"],
                    symbol=symbol,
                    transactions=response["data"]["symbols"][symbol],
                    current_prices=current_prices
                )
            else:
                logger.error(f"Got unowned symbol ({symbol})")
                return redirect(url_for("portfolio"))
        else:
            logger.error("Failed to retrieve portfolio data: " + response["error"])
            return redirect(url_for('index'))
    except InternalError:
        logger.debug(f"Communication between servers has failed: {response["internal_error"]}")
        return render_template(
            "users/portfolio.html",
            balance=0,
            symbols=None
        )
    except KeyError as error:
        logger.error(f"Own server error. Error: {error}")
        return redirect(url_for("portfolio"))
    except Exception as error:
        logger.error(f"Got bad response from own server: {error}")
    
    return redirect(url_for('index'))

@flask_app.route("/sign_in", methods=["GET", "POST"])
def sign_in() -> str:
    form = SignInForm()
    if request.method == "POST" and form.validate_on_submit():
        # communicate with fastAPI server to regiter the user
        response = get_response(endpoint=FastAPIRoutes.sign_in.value, method="post", data_to_send={"username": form.username.data, "password": form.password.data})
        logger.warning(f"Response: {response}")
        try:
            if "internal_error" in response.keys():
                raise InternalError
            if response["success"] is True:
                session["uuid"] = response["data"]["uuid"]
                session["email"] = response["data"]["email"]
                session["username"] = form.username.data
                session["password"] = form.password.data
                logger.debug(f"User {form.username.data} log in has been successful")
                return redirect(url_for("index"))
            else:
                logger.error(f"User {form.username.data} log in has failed")
                return redirect(url_for("sign_in", form=form, error=response["error"]))
        except InternalError as error:
            logger.debug(f"Communication between servers has failed: {response["internal_error"]}")
            return url_for("sign_in", form=form, error=response["internal_error"])
        except Exception as error:
            logger.error(f"Error: {error}")
        
        # Redirect to home page
        return redirect(url_for("sign_in"))
    else:
        # somehow return that passwords don't match then redirect to the same page
        logger.error(f"User {form.username.data} log in has failed miserably")
        return render_template("users/sign_in.html", form=form)

@flask_app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    form = SignUpForm()

    if request.method == "POST" and form.validate_on_submit() and form.password.data == form.repeat_password.data:
        # communicate with fastAPI server to regiter the user
        response = get_response(endpoint=FastAPIRoutes.sign_up.value, method="post", data_to_send={"email": form.email.data, "username": form.username.data, "password": form.password.data})
        
        try:
            if response["success"] == True:
                logger.debug(f"User {form.username.data} sign up has been successful")
            else:
                logger.error(f"User {form.username.data} sign up has failed")
        except InternalError:
            logger.debug(f"Communication between servers has failed: {response["internal_error"]}")
        except Exception as error:
            logger.error(f"Got bad response from other server: {error}")
        
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
    return render_template("users/profile_dashboard.html")

@flask_app.route('/update_user', methods=['GET', 'POST'])
def update_user():
    update_form = UpdateUserForm()

    if request.method == "POST" and update_form.validate_on_submit():
        if update_form.password.data != session["password"]:
            logger.warning(f"Password does not match session")
        else:
            attribute_to_update = update_form.attribute_to_update.data
            attribute_value = update_form.data[f"new_{attribute_to_update}"]

            response = get_response(endpoint=f"{FastAPIRoutes.update_user.value}/{attribute_to_update}", method="put", data_to_send={"value": attribute_value})

            try:
                response_json: dict = response.json()
                logger.debug(f"Got response from fastAPI server: {response.status_code}, {response_json}")
                if response_json["success"] == True:
                    logger.debug(f"User {session["username"]}'s update of {attribute_to_update} has been successful")
                    session[attribute_to_update] = attribute_value
                    logger.debug(f"User {attribute_to_update.capitalize()} is now {session[attribute_to_update]}")
                else:
                    logger.error(f"User {session["username"]} update of {update_form.attribute_to_update.data} has failed")
            except InternalError:
                logger.debug(f"Communication between servers has failed: {response["internal_error"]}")
            except Exception as error:
                logger.error(f"Got bad response from other server: {error}")
    else:
        logger.error(f"Update of user {session["username"]} failed")

    return render_template('users/update_user.html', update_form=UpdateUserForm())
         