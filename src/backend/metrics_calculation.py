import pandas as pd
import numpy as np


def transaction_level_metrics(transaction_data: pd.DataFrame, current_prices: pd.DataFrame):
    transaction_data_full = transaction_data.merge(current_prices, how="left", on="Ticker").fillna(0.0)
    return transaction_data_full


def calculate_lots(transaction_data: pd.DataFrame):
    transactions_dict = transaction_data\
        .sort_values(by="Transaction Date")\
        .to_dict(orient="records")

    lots = []

    for row in transactions_dict:
        ticker = row.get("Ticker")
        transaction_date = row.get("Transaction Date")
        quantity = row.get("Quantity")
        transaction_price = row.get("Transaction Price")
        fee = row.get("Fee")
        transaction_type = row.get("Transaction Type")

        if transaction_type == "BUY":
            # Open a new lot and instantiate some values based on the transaction
            lots.append({
                "Ticker": ticker,
                "Buy Date": transaction_date,
                "Initial Quantity": quantity,
                "Current Quantity": quantity,
                "Buy Price": transaction_price,
                "Buy Fee": fee,
                "Sell Fee": 0.0,
                "Realized PnL": 0.0,
                "Status": "OPEN",
            })

        elif transaction_type == "SELL":
            # Sell all quantity from as many lots as needed
            quantity_to_sell = quantity

            for lot in lots:
                if quantity_to_sell == 0:
                    # Nothing else to sell, go to next transaction
                    break

                if lot["Ticker"] == ticker and lot["Status"] == "OPEN":
                    # Applicable lot

                    if lot["Current Quantity"] >= quantity_to_sell:
                        # If the lot contains enough quantity, sell it.
                        quantity_sold = quantity_to_sell
                    else:
                        # Else sell all of it
                        quantity_sold = lot["Current Quantity"]

                    # Pro-Rata ratio calculation for sell fees
                    pro_rata_ratio = quantity_sold / quantity
                    pro_rata_sell_fee = fee * pro_rata_ratio

                    # Pro-Rata ratio calculation for buy fees
                    pro_rata_buy_fee = lot["Buy Fee"] * (quantity_sold / lot["Initial Quantity"])

                    # Update remaining lot quantity
                    lot["Current Quantity"] -= quantity_sold

                    # Update sell fees
                    lot["Sell Fee"] += pro_rata_sell_fee

                    # Realized PnL calculation
                    # Realized PnL = income - cost - sell fee - buy fee
                    income = quantity_sold * transaction_price
                    cost = quantity_sold * lot["Buy Price"]
                    lot["Realized PnL"] += (income - cost - pro_rata_sell_fee - pro_rata_buy_fee)

                    quantity_to_sell -= quantity_sold

                    if lot["Current Quantity"] == 0:
                        # Update lot status
                        lot["Status"] = "CLOSED"

    return pd.DataFrame(lots)


def calc_total_fees(lots_df: pd.DataFrame) -> pd.Series:
    return lots_df["Buy Fee"] + lots_df["Sell Fee"]


def calc_total_cost(lots_df: pd.DataFrame) -> pd.Series:
    return (lots_df["Initial Quantity"] * lots_df["Buy Price"]) + lots_df["Total Fees"]


def calc_current_market_value(lots_df: pd.DataFrame, current_prices: pd.DataFrame) -> pd.Series:
    lots_df = lots_df.merge(current_prices, how="left", on="Ticker")
    return lots_df["Current Quantity"] * lots_df["Current Price"]


def calc_unrealized_pnl(lots_df: pd.DataFrame, current_prices: pd.DataFrame) -> pd.Series:
    lots_df = lots_df.merge(current_prices, how="left", on="Ticker")
    
    current_value = lots_df["Current Quantity"] * lots_df["Current Price"]
    cost_of_remaining = lots_df["Current Quantity"] * lots_df["Buy Price"]
    remaining_buy_fees = lots_df["Buy Fee"] * (lots_df["Current Quantity"] / lots_df["Initial Quantity"])
    
    return current_value - cost_of_remaining - remaining_buy_fees


def calc_days_held(lots_df: pd.DataFrame, as_of_date: pd.Timestamp = None) -> pd.Series:
    if as_of_date is None:
        as_of_date = pd.Timestamp.today()
    
    buy_dates = pd.to_datetime(lots_df["Buy Date"])
    return (as_of_date - buy_dates).dt.days


def calc_total_pnl(lots_df: pd.DataFrame) -> pd.Series:
    return lots_df["Realized PnL"] + lots_df["Unrealized PnL"]


def calc_total_roi(lots_df: pd.DataFrame) -> pd.Series:
    # ROI = (Total PnL / Total Cost) * 100
    return np.where(lots_df["Total Cost"] > 0, (lots_df["Total PnL"] / lots_df["Total Cost"]) * 100, 0)


def calc_annualized_gain(lots_df: pd.DataFrame) -> pd.Series:
    # annualized gain = (((current value + realized pnl) / total cost) ^ 365 / days held) - 1
        
    numerator = lots_df["Current Market Value"] + lots_df["Realized PnL"]
    denominator = lots_df["Total Cost"]
    power = 365 / lots_df["Days Held"]

    return np.where((lots_df["Total Cost"] > 0) & (lots_df["Days Held"] >= 365), 100 * ((numerator / denominator) ** power - 1), np.nan)


def calc_unrealized_pnl_pct(lots_df: pd.DataFrame) -> pd.Series:
    remaining_buy_fees = lots_df["Buy Fee"] * (lots_df["Current Quantity"] / lots_df["Initial Quantity"])
    cost_of_remaining = (lots_df["Current Quantity"] * lots_df["Buy Price"]) + remaining_buy_fees
    cost_of_remaining = np.where(cost_of_remaining > 0, cost_of_remaining, np.nan)
    return(lots_df["Unrealized PnL"] / cost_of_remaining) * 100


def calc_realized_pnl_pct(lots_df: pd.DataFrame) -> pd.Series:
    sold_qty = lots_df["Initial Quantity"] - lots_df["Current Quantity"]
    
    sold_buy_fees = lots_df["Buy Fee"] * (sold_qty / lots_df["Initial Quantity"])
    cost_of_sold = (sold_qty * lots_df["Buy Price"]) + sold_buy_fees + lots_df["Sell Fee"]
    
    return np.where(cost_of_sold > 0, (lots_df["Realized PnL"] / cost_of_sold) * 100, np.nan)


def lot_level_metrics(transaction_data: pd.DataFrame, current_prices: pd.DataFrame):
    lots = calculate_lots(transaction_data)
    lots["Total Fees"] = calc_total_fees(lots)
    lots["Total Cost"] = calc_total_cost(lots)
    lots["Current Market Value"] = calc_current_market_value(lots, current_prices)
    lots["Unrealized PnL"] = calc_unrealized_pnl(lots, current_prices)
    lots["Days Held"] = calc_days_held(lots)
    lots["Total PnL"] = calc_total_pnl(lots)
    lots["Total ROI %"] = calc_total_roi(lots)
    lots["Annualized Gain %"] = calc_annualized_gain(lots)
    lots["Unrealized PnL %"] = calc_unrealized_pnl_pct(lots)
    lots["Realized PnL %"] = calc_realized_pnl_pct(lots)
    return lots


