from datetime import timedelta
from typing import Union
from collections import defaultdict

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

from routes.utils.user_feedbacks import UserFeedbacks
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
    return render_template("index.html")

@flask_app.route("/readme", methods=["GET"])
def readme() -> str:
    return get_rendered_readme()

@flask_app.route('/stock_dashboard/', methods=['GET', 'POST'])    
@flask_app.route('/stock_dashboard/<symbol>', methods=['GET', 'POST'])
# @sign_in_required()
def stock_dashboard(symbol: str = None):
    if symbol is None:
        return redirect(f"{url_for('stock_dashboard')}/AAPL")
    
    # Got symbol already
    symbol = symbol.upper()
    
    try:
        symbol_form = SymbolPickForm()
        feedback = None
        trade_feedback = None
        keep_form_data = True


        # Symbol form part
        if request.method == "POST" and symbol_form.validate_on_submit():
            # Handle symbol selection logic
            selected_symbol = symbol_form.symbol.data.upper()
            return redirect(f"{url_for("stock_dashboard")}/{selected_symbol}")
        

        # Tradeform part
        trade_form = TradeForm()

        # Verify symbol exists / is compatable with website
        info = get_symbol_info(symbol)
        info_keys_list = list(info.keys())
        if "bid" not in info_keys_list or "ask" not in info_keys_list:
            info = None

        if request.method == "POST" and trade_form.validate_on_submit() and info is not None:
            logger.debug(f"Trade form submitted")
            order = trade_form.data
            order["symbol"] = symbol
            logger.debug(f"Submitting form to server: {order}")
            # Submit order to server
            response = get_response(
                endpoint=FastAPIRoutes.submit_order.value, 
                method="post", 
                data_to_send={"order": order}
            )

            try:
                if "internal_error" in response.keys():
                    raise InternalError
                if response["success"] is True:
                    logger.info(f"Order for {order["shares"]} shares of {order["symbol"]} has been successful")
                    trade_feedback = response["data"]
                    keep_form_data = False
                else:
                    logger.error(f"Order {order} has failed")
                    trade_feedback = response["error"]
            except InternalError:
                logger.debug(f"Communication between servers has failed: {response["internal_error"]}")
                trade_feedback = UserFeedbacks.internal_error.value
            except KeyError as error:
                logger.error(f"Got bad response from other server: {error}")
                trade_feedback = UserFeedbacks.internal_error.value
            except Exception as error:
                logger.error(f"Error: {error}")
                feedback = UserFeedbacks.internal_error.value
        elif info is None:
            raise InternalError("Stock does not exist")
        
        if not keep_form_data:
            trade_form = TradeForm(formdata=None)
        
        return render_template(
            "stocks/stock_dashboard.html", 
            trade_form=trade_form,
            symbol_form=symbol_form,
            symbol=symbol,
            bid=info["bid"],
            ask=info["ask"],
            feedback=feedback,
            trade_feedback=trade_feedback
        )
    except InternalError as error:
        logger.warning(f"InternalError: {error}")
        return render_template(
            "stocks/stock_dashboard.html", 
            trade_form=get_locked_trade_form(), 
            symbol_form=symbol_form,
            symbol="Invalid Symbol",
            feedback=feedback,
            trade_feedback=trade_feedback
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

@flask_app.route('/my/dashboard')
@sign_in_required()
def profile():
    return render_template("users/profile.html")

# Fully Complete
@flask_app.route("/sign_in", methods=["GET", "POST"])
def sign_in() -> str:
    sign_in_form = SignInForm()
    keep_form_data = True
    redirect_profile = False

    if request.method == "POST" and sign_in_form.validate_on_submit():
        # Communicate with fastAPI server to sign in the user
        response = get_response(
            endpoint=FastAPIRoutes.sign_in.value, 
            method="post", 
            data_to_send={"username": sign_in_form.username.data, "password": sign_in_form.password.data}
        )
        try:
            if "internal_error" in response.keys():
                raise InternalError
            
            if response["success"] is True:
                # Add user info to session
                session["uuid"] = response["data"]["uuid"]
                session["email"] = response["data"]["email"]
                session["username"] = sign_in_form.username.data
                session["password"] = sign_in_form.password.data

                logger.debug(f"User {sign_in_form.username.data} sign in has been successful")
                feedback = "Sign In Has Been Successful"
                keep_form_data = False
                redirect_profile = True
            else:
                logger.error(f"User {sign_in_form.username.data} sign in has failed")
                feedback = response["error"]
        except InternalError as error:
            logger.debug(f"Communication between servers has failed: {response["internal_error"]}")
            feedback = UserFeedbacks.internal_error.value
        except KeyError as error:
            logger.error(f"Got bad response from other server: {error}")
            feedback = UserFeedbacks.internal_error.value
        except Exception as error:
            logger.error(f"Error: {error}")
            feedback = UserFeedbacks.internal_error.value
    elif request.method == "GET":
        return render_template("users/sign_in.html", form=sign_in_form)
    else:
        logger.error(f"User {sign_in_form.username.data} sign in has failed miserably")
        feedback = UserFeedbacks.something_wrong.value
    
    if not keep_form_data:
        sign_in_form = SignInForm(formdata=None)

    return render_template(
        "users/sign_in.html", 
        form=sign_in_form,
        feedback=feedback,
        redirect_profile=redirect_profile
    )

# Fully Complete
@flask_app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    sign_up_form = SignUpForm()
    feedback = None
    keep_form_data = True
    redirect_home = False

    if request.method == "POST" and sign_up_form.validate_on_submit() and sign_up_form.password.data == sign_up_form.repeat_password.data:
        # Communicate with fastAPI server to regiter the user
        response = get_response(
            endpoint=FastAPIRoutes.sign_up.value, 
            method="post", 
            data_to_send={"email": sign_up_form.email.data, "username": sign_up_form.username.data, "password": sign_up_form.password.data}
        )
        try:
            if response["success"] == True:
                logger.debug(f"User {sign_up_form.username.data} sign up has been successful")
                feedback = "User Sign Up Has Been Successful"
                keep_form_data = False
                redirect_home = True
            else:
                logger.error(f"User {sign_up_form.username.data} sign up has failed")
                feedback = response["error"]
        except InternalError:
            logger.debug(f"Communication between servers has failed: {response["internal_error"]}")
            feedback = UserFeedbacks.internal_error.value
            keep_form_data = True
        except KeyError as error:
            logger.error(f"Got bad response from other server: {error}")
            feedback = UserFeedbacks.internal_error.value
            keep_form_data = True
        except Exception as error:
            logger.error(f"Error: {error}")
            feedback = UserFeedbacks.internal_error.value
            keep_form_data = True
    elif sign_up_form.validate_on_submit() and sign_up_form.password.data != sign_up_form.repeat_password.data:
        feedback = UserFeedbacks.password_not_match.value
    elif request.method == "GET":
        return render_template("users/sign_up.html", form=sign_up_form)
    else:
        logger.error(f"User {sign_up_form.username.data} sign up has failed miserably")
        feedback = UserFeedbacks.something_wrong.value
    
    if not keep_form_data:
        sign_up_form = SignUpForm(formdata=None)
    return render_template(
        "users/sign_up.html", 
        form=sign_up_form,
        feedback=feedback,
        redirect_home=redirect_home
    )

@flask_app.route('/sign_out')
@sign_in_required()
def sign_out():
    session.pop("username", None)
    session.pop("password", None)
    session.pop("uuid", None)

    return redirect(url_for("index"))


@flask_app.route('/update_user', methods=['GET', 'POST'])
def update_user():
    update_form = UpdateUserForm()
    feedback = None
    keep_form_data = True

    if request.method == "POST" and update_form.validate_on_submit():
        if update_form.password.data != session["password"]:
            logger.warning(f"Password does not match session")
            feedback = UserFeedbacks.password_not_match.value
        else:
            attribute_to_update = update_form.attribute_to_update.data
            attribute_value = update_form.data[f"new_{attribute_to_update}"]

            # Communicate with fastAPI server to update the user
            response = get_response(
                endpoint=f"{FastAPIRoutes.update_user.value}/{attribute_to_update}", 
                method="put", 
                data_to_send={"value": attribute_value}
            )

            try:
                if response["success"] == True:
                    session[attribute_to_update] = attribute_value
                    logger.debug(f"User {session["username"]}'s update of {attribute_to_update} has been successful")
                    logger.debug(f"User {attribute_to_update.capitalize()} is now {session[attribute_to_update]}")
                    feedback = f"Successfully changed {attribute_to_update.capitalize()}"
                    keep_form_data = False
                else:
                    logger.error(f"User {session["username"]} update of {update_form.attribute_to_update.data} has failed")
                    feedback = response["error"]
            except InternalError as error:
                logger.debug(f"Communication between servers has failed: {response["internal_error"]}")
                feedback = UserFeedbacks.internal_error.value
            except KeyError as error:
                logger.error(f"Got bad response from other server: {error}")
                feedback = UserFeedbacks.internal_error.value
            except Exception as error:
                logger.error(f"Error: {error}")
                feedback = UserFeedbacks.internal_error.value
    elif request.method == "GET":
        return render_template("users/update_user.html", form=update_form)
    else:
        logger.error(f"Update of user {session["username"]} sign up has failed miserably")
        feedback = UserFeedbacks.something_wrong.value
    
    if not keep_form_data:
        update_form = UpdateUserForm(formdata=None)
    return render_template(
        "users/update_user.html", 
        form=update_form,
        feedback=feedback
    )
      