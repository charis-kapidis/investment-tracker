import yfinance as yf
import pandas as pd
import logging

logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

def get_current_prices(tickers: list) -> dict:
    prices_dict = {}

    if not tickers:
        logging.warning("The list of tickers is empty. No Yahoo Finance call.")
        return prices_dict

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")

            if hist.empty:
                logging.warning(f"No data available for ticker {ticker}. Possibly spelling mistake or delistig.")
                prices_dict[ticker] = 0.0
            else:
                current_price = float(hist['Close'].iloc[-1])
                prices_dict[ticker] = current_price

        except Exception as e:
            logging.error(f"Unexpected error while getting data for ticker {ticker}: {e}")
            prices_dict[ticker] = 0.0

    return prices_dict
