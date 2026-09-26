import streamlit as st
import pandas as pd

from src.backend.input_handler import input_handling
from src.backend.market_data import get_current_prices
from src.backend.metrics_calculation import transaction_level_metrics, lot_level_metrics, asset_level_metrics, portfolio_level_metrics

st.title("Welcome to Portfolio Tracker 📈")
st.write("Upload your file with transaction data to begin the analysis.")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    if st.button("Data Analysis"):
        
        with st.spinner("Calculating metrics..."):
            
            transaction_data, tickers = input_handling(uploaded_file)
            current_prices = get_current_prices(tickers)
            transaction_data = transaction_level_metrics(transaction_data, current_prices)
            lot_data_present, lot_data_full = lot_level_metrics(transaction_data, current_prices)
            asset_data_present, asset_data_full = asset_level_metrics(lot_data_full, transaction_data)
            portfolio_data_present, portfolio_datafull = portfolio_level_metrics(asset_data_full, transaction_data)
            
            st.session_state['portfolio_df'] = portfolio_data_present
            st.session_state['asset_df'] = asset_data_present
            st.session_state['lot_df'] = lot_data_present
            st.session_state['transaction_df'] = transaction_data
            
            st.success("Calculating metrics completed!")
            
            st.switch_page("src/frontend/portfolio.py")
            