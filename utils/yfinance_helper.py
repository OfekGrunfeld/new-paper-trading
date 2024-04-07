from typing import Union

import yfinance as yf

from utils.logger_script import logger


def get_symbol_info(symbol: str) -> Union[dict, None]:
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