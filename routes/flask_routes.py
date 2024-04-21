from requests import Response

from flask import current_app as flask_app
from flask import render_template, redirect, session
from flask.helpers import url_for

from utils.render_readme import get_rendered_readme 
from utils import logger, yfinance_helper
from forms.stocks_logic import SymbolPickForm, TradeForm, get_locked_trade_form
from comms import submit_order
from routes.utils.auth import sign_in_required, redirect_to_access_denied


@flask_app.route("/")
def index() -> str:
    return get_rendered_readme()
    
@flask_app.route('/stock_dashboard', methods=['GET'])
@flask_app.route('/stock_dashboard/', methods=['GET'])
@flask_app.route('/stock_dashboard/<symbol>', methods=['GET', 'POST'])
@sign_in_required()
def stock_dashboard(symbol: str = None):
    if symbol is None:
        return redirect_to_access_denied(reason="Choose a symbol")
    
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
                if response_json["success"] is True:
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