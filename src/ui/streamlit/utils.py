import streamlit as st
import pandas as pd
import plotly.express as px

from src.backend.input_handler import input_handling
from src.backend.market_data import get_current_prices
from src.backend.metrics_calculation import transaction_level_metrics, lot_level_metrics, asset_level_metrics, portfolio_level_metrics


HOMEPAGE = "src/ui/streamlit/home.py"
PORTFOLIO = "src/ui/streamlit/portfolio.py"
ASSET = "src/ui/streamlit/asset.py"
LOT = "src/ui/streamlit/lot.py"
TRANSACTION = "src/ui/streamlit/transaction.py"
DEMO_FILENAME = "dummy_transactions.csv"
SCHEMA_EXAMPLE = pd.DataFrame({
        "Transaction Date": ["2023-01-15", "2023-02-20"],
        "Portfolio": ["Main", "Retirement"],
        "Ticker": ["AAPL", "BTC"],
        "Transaction Type": ["BUY", "SELL"],
        "Quantity": [10, 0.5],
        "Transaction Price": [150.00, 22000.00],
        "Fee": [1.50, 5.00]
    })


def load_data(file):
    transaction_data, tickers = input_handling(file)
    current_prices = get_current_prices(tickers)
    transaction_data = transaction_level_metrics(transaction_data, current_prices)
    lot_data_present, lot_data_full = lot_level_metrics(transaction_data, current_prices)
    asset_data_present, asset_data_full = asset_level_metrics(lot_data_full, transaction_data)
    portfolio_data_present, portfolio_data_full = portfolio_level_metrics(asset_data_full, transaction_data)

    st.session_state["portfolio_df"] = portfolio_data_present
    st.session_state["asset_df"] = asset_data_present
    st.session_state["lot_df"] = lot_data_present
    st.session_state["transaction_df"] = transaction_data


def style_pnl(val):
    if isinstance(val, (int, float)):
        if val > 0:
            return "background-color: rgba(39, 174, 96, 0.2)" # Απαλό πράσινο
        elif val < 0:
            return "background-color: rgba(231, 76, 60, 0.2)" # Απαλό κόκκινο
    return ""


def verify_data_availability(session_state):
    if "portfolio_df" not in session_state or "asset_df" not in session_state or "lot_df" not in session_state or "transaction_df" not in session_state:
        st.warning("Please upload your transaction data CSV file.")
        if st.button("Homepage"):
            st.switch_page(HOMEPAGE)
        st.stop()


def create_portfolio_dropdown(transaction=False):
    portfolios = st.session_state["asset_df"]["Portfolio"].unique().tolist()
    
    if transaction:
        portfolios = ["All"] + portfolios
    
    default_index = 0
    if "selected_portfolio" in st.session_state and st.session_state["selected_portfolio"] in portfolios:
        default_index = portfolios.index(st.session_state["selected_portfolio"])

    selected_portfolio = st.selectbox("Choose a portfolio for further analysis:", options=portfolios, index=default_index)

    return selected_portfolio


def create_asset_dropdown(transaction=False):
    if st.session_state["selected_portfolio"] != "All":
        assets = st.session_state["asset_df"][st.session_state["asset_df"]["Portfolio"] == st.session_state["selected_portfolio"]]["Ticker"].unique().tolist()
    else:
        assets = st.session_state["transaction_df"]["Ticker"].unique().tolist()
    
    if transaction:
        assets = ["All"] + assets        

    asset_index = 0
    if "selected_asset" in st.session_state and st.session_state["selected_asset"] in assets:
        asset_index = assets.index(st.session_state["selected_asset"])

    selected_asset = st.selectbox("Choose an asset for further analysis:", options=assets, index=asset_index)

    return selected_asset


def create_type_dropdown(transaction=False):
    types = ["All"] + st.session_state["transaction_df"]["Transaction Type"].unique().tolist()
    
    selected_type = st.selectbox("Transaction Type", options=types, index=0)

    return selected_type


def create_date_range_dropdown(transaction=False):
    min_date, max_date = st.session_state["transaction_df"]["Transaction Date"].min().date(), st.session_state["transaction_df"]["Transaction Date"].max().date()

    selected_date_range = st.date_input(
        "Transaction Date", 
        value=(min_date, max_date), 
        min_value=min_date, 
        max_value=max_date
    )
    return selected_date_range
