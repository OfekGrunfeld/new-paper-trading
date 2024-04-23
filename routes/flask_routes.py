from typing import List, Dict, Union
from collections import defaultdict

from requests import Response

from flask import current_app as flask_app
from flask import render_template, redirect, session
from flask.helpers import url_for

from utils.render_readme import get_rendered_readme 
from utils.logger_script import logger
from utils.yfinance_helper import get_current_prices_of_symbol_list, get_symbol_info
from forms.stocks_logic import SymbolPickForm, TradeForm, get_locked_trade_form
from comms.communications import submit_order, get_portfolio
from routes.utils.auth import sign_in_required, redirect_to_access_denied


@flask_app.route("/")
def index() -> str:
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

    
    trade_form = TradeForm()
    if trade_form.validate_on_submit():
        logger.debug(f"Trade form submitted")

        logger.debug(f"Submitting form to server")
        order = trade_form.data
        order["symbol"] = symbol
        response = submit_order(order)
        if isinstance(response, Response):
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

@flask_app.route('/portfolio', methods=['GET'])            
@flask_app.route('/portfolio/', methods=['GET'])      
@flask_app.route('/portfolio/<symbol>', methods=['GET'])    
@sign_in_required()
def portfolio(symbol: str = None):
    if symbol is not None:
        symbol = symbol.upper()
    response = get_portfolio()
    if isinstance(response, Response):
        try:
            response_json = response.json()
            if response_json["success"]:
                current_prices = get_current_prices_of_symbol_list(response_json["data"]["symbols"].keys())
                if symbol is None:
                    symbols: dict[str, list[dict[str, Union[str, float]]]]= response_json["data"]["symbols"]           

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
                    
                    return render_template(
                        "users/portfolio.html",
                        balance=response_json["data"]["balance"],
                        symbols=response_json["data"]["symbols"],
                        total_shares=total_shares,
                        total_worths=total_worths
                    )
                elif symbol in response_json["data"]["symbols"]:
                    return render_template(
                        "users/stock.html",
                        balance=response_json["data"]["balance"],
                        symbol=symbol,
                        transactions=response_json["data"]["symbols"][symbol],
                        current_prices=current_prices
                    )
                else:
                    logger.error(f"Got unowned symbol ({symbol})")
                    return redirect(url_for("portfolio"))
            else:
                logger.error("Failed to retrieve portfolio data: " + response_json["error"])
                return redirect(url_for('index'))
        except KeyError as error:
            logger.error(f"Own server error. Error: {error}")
            return redirect(url_for("portfolio"))
        except Exception as error:
            logger.error(f"Got bad response from own server: {error}")
            import traceback
            logger.error(f"{traceback.format_exc()}")
    elif isinstance(response, dict):
        try:
            logger.debug(f"Communication between servers has failed: {response["internal_error"]}")
            return render_template(
                "users/portfolio.html",
                balance=0,
                symbols=None
            )
        except Exception as error:
            logger.error(f"Got bad response from own server: {error}")
    
    return redirect(url_for('index'))
        

    