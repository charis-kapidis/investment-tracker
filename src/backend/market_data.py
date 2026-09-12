import yfinance as yf
import pandas as pd
import logging

logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

def get_current_prices(tickers: list) -> dict:
    if not tickers:
        logging.warning("The list of tickers is empty. No Yahoo Finance call.")
        raise ValueError("The list of tickers is empty. No Yahoo Finance call.")

    tickers = yf.Tickers(tickers)

    # Getting historic values
    # Resetting index to access specific values
    # Transpose to create a row per ticker
    # Resetting index to create a column for all tickers
    # Dropping date row
    # Renaming values column
    # Filling NA values with zero
    current_price_df = tickers\
        .history(period="1d")["Close"]\
        .reset_index(drop=False)\
        .T\
        .reset_index(drop=False)\
        .drop(index=0)\
        .rename(mapper={0: "Current Price"}, axis=1)\
        .fillna(0.0)
    
    return current_price_df
