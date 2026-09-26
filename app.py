from src.backend.input_handler import input_handling
from src.backend.market_data import get_current_prices
from src.backend.metrics_calculation import transaction_level_metrics, lot_level_metrics, asset_level_metrics, portfolio_level_metrics

def main():
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

if __name__ == "__main__":
    main()