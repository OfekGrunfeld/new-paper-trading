from typing import Union

import yfinance as yf

from utils.logger_script import logger

def get_symbol_info(symbol: str) -> Union[dict, None]:
    """
    Retrieves detailed financial information about a given symbol using yfinance's info attribute.

    Parameters:
        symbol (str): The stock symbol to retrieve information for.

    Returns:
        Union[dict, None]: A dictionary containing financial details about the symbol if successful, None otherwise.
    
    Notes:
        - This function might return an empty dictionary as a special case where a symbol doesn't exist.
    """
    if symbol is None:
        logger.error(f"Entered symbol is None")
    try:
        ticker = yf.Ticker(symbol)
    except Exception as error:
        logger.error(f"Tried getting info for probably non-existent symbol: {symbol}.\nError:{error}")
        return None
    try:
        info = ticker.info
        return info
    except Exception as error:
        logger.error(f"222 Tried getting info for probably non-existent symbol: {symbol}.\nError:{error}")
        return None

def get_current_prices_of_symbol_list(symbols: list[str]) -> dict[str, float]:
    """
    Retrieves the current price for a list of stock symbols.

    Parameters:
        symbols (list[str]): A list of stock symbols to retrieve current prices for.

    Returns:
        dict[str, Union[float, None]]: A dictionary mapping each symbol to its current price or None if an error occurred.
    
    Notes:
        - If an error occurs during fetching, the value for that symbol is set to None.
    """
    
    values = []
    for symbol in symbols:
        try:
            symbol_info = get_symbol_info(symbol)
            try:
                current_price = symbol_info["currentPrice"]
                values.append(current_price)
            except Exception as error:
                logger.error(f"Couldn't get current price for {symbol}")
                values.append(None)
        except Exception as error:
            logger.error(f"Couldn't get symbol info for {symbol}")
            values.append(None)
            
    return dict(zip(symbols,values))

