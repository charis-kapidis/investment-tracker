import streamlit as st

from src.backend.input_handler import input_handling
from src.backend.market_data import get_current_prices
from src.backend.metrics_calculation import transaction_level_metrics, lot_level_metrics, asset_level_metrics, portfolio_level_metrics

def main_terminal():
    print("Hello from investment-tracker!")
    transactions_filename = input("Provide the name of the file containing the transactions: ")
    transaction_data, tickers = input_handling(transactions_filename)
    current_prices = get_current_prices(tickers)
    transaction_data = transaction_level_metrics(transaction_data, current_prices)
    lot_data_present, lot_data_full = lot_level_metrics(transaction_data, current_prices)
    asset_data_present, asset_data_full = asset_level_metrics(lot_data_full, transaction_data)
    portfolio_data_present, portfolio_datafull = portfolio_level_metrics(asset_data_full, transaction_data)

    print("\n")
    print(lot_data_present)
    print(asset_data_present)
    print(portfolio_data_present)


def main_streamlit():
    st.set_page_config(
        page_title="Portfolio Tracker",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    pages = {
        "Menu": [
            st.Page("src/ui/streamlit/home.py", title="Homepage - Upload", icon="🏠"),
            st.Page("src/ui/streamlit/portfolio.py", title="Portfolios", icon="💼"),
            st.Page("src/ui/streamlit/asset.py", title="Assets", icon="📊"),
            st.Page("src/ui/streamlit/lot.py", title="Lots", icon="📦"),
            st.Page("src/ui/streamlit/transaction.py", title="Transactions", icon="📝"),
        ]
    }

    pg = st.navigation(pages)
    pg.run()

# if __name__ == "__main__":
#     main_terminal()

if __name__ == "__main__":
    main_streamlit()