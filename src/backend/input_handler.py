from pathlib import Path
import pandas as pd
import time
import logging


DEFAULT_FILENAME = "dummy_transactions.csv"

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_COLUMNS = [
    "Portfolio", 
    "Transaction Date", 
    "Transaction Type", 
    "Ticker", 
    "Quantity", 
    "Transaction Price", 
    "Fee"
]

REQUIRED_DATA_TYPES_CHECKS = {
    "Portfolio": lambda x: isinstance(x, str) or isinstance(x, int),                        # string or integer
    "Transaction Date": lambda x: 
        (pd.to_datetime(x, format="%Y%m%d", errors="coerce") is not pd.NaT) or 
        (pd.to_datetime(x, format="%Y-%m-%d", errors="coerce") is not pd.NaT),              # format should match YYYY-MM-DD or YYYYMMDD
    "Transaction Type": lambda x: isinstance(x, str),                                       # string
    "Ticker": lambda x: isinstance(x, str),                                                 # string
    "Quantity": lambda x: isinstance(x, int),                                               # integet
    "Transaction Price": lambda x: (isinstance(x, float) or isinstance(x, int)),            # float or integer
    "Fee": lambda x: (isinstance(x, float) or isinstance(x, int))                           # float or integer
}

REQUIRED_DATA_TYPES = {
    "Portfolio": str, 
    "Transaction Date": str,
    "Transaction Type": str,
    "Ticker": str,
    "Quantity": int,
    "Transaction Price": float,
    "Fee": float
}

REQUIRED_DATA_VALIDITY_RULES = {
    "Portfolio": lambda x: len(x) > 0,                                                  # at least one character long
    "Transaction Date": lambda x: x <= pd.to_datetime(time.ctime()),                    # date before current time
    "Transaction Type": lambda x: x in ["BUY", "SELL"],                                 # available values: BUY, SELL
    "Ticker": lambda x: len(x) > 0,                                                     # at least one character long
    "Quantity": lambda x: x > 0,                                                        # positive number
    "Transaction Price": lambda x: x >= 0,                                              # non-negative number
    "Fee": lambda x: x >= 0                                                             # non-negative number
}

TICKER_COLUMN = "Ticker"


logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


def load_transactional_data(filename):
    if isinstance(filename, str):
        data_folder = "data"
        file_path = PROJECT_ROOT / data_folder / "demo" / filename
        try:
            data = pd.read_csv(file_path)
            # print("✅ File loaded successfully\n")
            logging.info(f"File loaded successfully")
        except Exception as e:
            # print(f"❌ Error: {e}")
            logging.warning(f"File not loaded")
    else:
        data = pd.read_csv(filename)
    return data


def check_required_columns(data: pd.DataFrame):
    required_columns = REQUIRED_COLUMNS

    missing_columns = []
    for col in required_columns:
        if col not in data.columns:
            missing_columns.append(col)

    if missing_columns:
        logging.warning(f"Required columns missing from data")
        raise ValueError(f"❌ The following columns are missing from the data: {missing_columns}")

    data = data[required_columns]
    logging.info(f"File contains all required columns")
    # print("✅ File contains all required columns!\n")
    return data


def check_data_types(data: pd.DataFrame):
    required_data_type_checks = REQUIRED_DATA_TYPES_CHECKS

    data_types_violated = []
    for col in required_data_type_checks:
        if not all(data[col].apply(required_data_type_checks[col])):
            data_types_violated.append(col)

    if data_types_violated:
        logging.warning(f"Failed some data type rules")
        raise ValueError(f"❌ Some values in columns {data_types_violated} do not meet the required data type rules.")
               
    required_data_types = REQUIRED_DATA_TYPES

    data = data.astype(required_data_types)           
               
    if any(data["Transaction Date"].apply(lambda x: (pd.to_datetime(x, format="%Y%m%d", errors="coerce") is not pd.NaT))):
        data["Transaction Date"] = pd.to_datetime(data["Transaction Date"], format="%Y%m%d", errors="coerce")
    else:
        data["Transaction Date"] = pd.to_datetime(data["Transaction Date"], format="%Y-%m-%d", errors="coerce")          

    logging.info(f"Passed all data type rules")
    # print("✅ Passed all data type rules!\n")
    return data


def check_data_validity(data: pd.DataFrame):
    required_data_validity = REQUIRED_DATA_VALIDITY_RULES

    rules_violated = []
    for col in required_data_validity:
        if not all(data[col].apply(required_data_validity[col])):
            rules_violated.append(col)

    if rules_violated:
        logging.warning(f"Failed some data validity rules")
        raise ValueError(f"❌ Some values in columns {rules_violated} do not meet the required rules.")

    data["Ticker"] = data["Ticker"].str.strip().str.upper()

    logging.info(f"Passed all data validity rules")
    # print("✅ Passed all data validity rules!\n")
    return data


def get_tickers(data: pd.DataFrame):
    tickers = data[TICKER_COLUMN].unique().tolist()
    return tickers

def input_handling(filename):
    if filename == "":
        filename = DEFAULT_FILENAME

    data = load_transactional_data(filename)
    data = check_required_columns(data)
    data = check_data_types(data)
    data = check_data_validity(data)
    tickers = get_tickers(data)

    return data, tickers


if __name__ == "__main__":
    print(input_handling(DEFAULT_FILENAME).head(1))