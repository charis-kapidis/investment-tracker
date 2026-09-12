import pandas as pd


def transaction_level_metrics(transaction_data: pd.DataFrame, current_prices: pd.DataFrame):
    transaction_data_full = transaction_data.merge(current_prices, how="left", on="Ticker").fillna(0.0)
    return transaction_data_full