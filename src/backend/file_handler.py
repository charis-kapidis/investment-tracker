from pathlib import Path
import pandas as pd
import time
import logging


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
        (pd.to_datetime(x, format='%Y%m%d', errors='coerce') is not pd.NaT) or 
        (pd.to_datetime(x, format='%Y-%m-%d', errors='coerce') is not pd.NaT),              # format should match YYYY-MM-DD or YYYYMMDD
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


logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')


def load_raw_data(filename: str):
    data_folder = "data"
    file_path = PROJECT_ROOT / data_folder / "raw" / filename
    try:
        data = pd.read_csv(file_path)
    except Exception as e:
        print(f"❌ Error: {e}")

    print("✅ File loaded successfully!\n")
    return data


def check_required_columns(data: pd.DataFrame):
    required_columns = REQUIRED_COLUMNS

    missing_columns = []
    for col in required_columns:
        if col not in data.columns:
            missing_columns.append(col)

    if missing_columns:
        raise ValueError(f"❌ The following columns are missing from the data: {missing_columns}")

    data = data[required_columns]
    print("✅ File contains all required columns!\n")
    return data


def check_data_types(data: pd.DataFrame):
    required_data_type_checks = REQUIRED_DATA_TYPES_CHECKS

    data_types_violated = []
    for col in required_data_type_checks:
        if not all(data[col].apply(required_data_type_checks[col])):
            data_types_violated.append(col)

    if data_types_violated:
        raise ValueError(f"❌ Some values in columns {data_types_violated} do not meet the required data type rules.")
               
    required_data_types = REQUIRED_DATA_TYPES

    data = data.astype(required_data_types)           
               
    if any(data["Transaction Date"].apply(lambda x: (pd.to_datetime(x, format='%Y%m%d', errors='coerce') is not pd.NaT))):
        data["Transaction Date"] = pd.to_datetime(data["Transaction Date"], format='%Y%m%d', errors='coerce')
    else:
        data["Transaction Date"] = pd.to_datetime(data["Transaction Date"], format='%Y-%m-%d', errors='coerce')          

    print("✅ Passed all data type rules!\n")
    return data


def check_data_validity(data: pd.DataFrame):
    required_data_validity = REQUIRED_DATA_VALIDITY_RULES

    rules_violated = []
    for col in required_data_validity:
        if not all(data[col].apply(required_data_validity[col])):
            rules_violated.append(col)

    if rules_violated:
        raise ValueError(f"❌ Some values in columns {rules_violated} do not meet the required rules.")

    data["Ticker"] = data["Ticker"].str.strip().str.upper()

    print("✅ Passed all data validity rules!\n")
    return data


def load_transactional_data(filename: str):
    pass

if __name__ == "__main__":
    filename = "portfolio - portfolio.csv"

    data = load_transactional_data(filename)
    data = check_required_columns(data)
    data = check_data_types(data)
    data = check_data_validity(data)






import pandas as pd
import os
import logging

# Ρύθμιση του logger για την καταγραφή σφαλμάτων
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

def load_transactions(filepath: str) -> pd.DataFrame:
    """
    Διαβάζει, καθαρίζει και επικυρώνει το CSV των συναλλαγών.
    
    Args:
        filepath (str): Η διαδρομή για το αρχείο CSV.
        
    Returns:
        pd.DataFrame: Ένα καθαρό dataframe έτοιμο για ανάλυση.
    """
    # 1. Έλεγχος αν υπάρχει το αρχείο (ή αν το αντικείμενο είναι file-like object από το Streamlit)
    if isinstance(filepath, str) and not os.path.exists(filepath):
        raise FileNotFoundError(f"Το αρχείο δεν βρέθηκε στη διαδρομή: {filepath}")

    # 2. Φόρτωση δεδομένων
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        raise ValueError(f"Σφάλμα κατά την ανάγνωση του CSV: {e}")

    # 3. Καθαρισμός ονομάτων στηλών (αφαίρεση κενών)
    df.columns = df.columns.str.strip()

    # Ορίζουμε τις στήλες που περιμένουμε υποχρεωτικά
    required_columns = ['Date', 'Ticker', 'Action', 'Quantity', 'Price', 'Fees']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Λείπουν οι εξής υποχρεωτικές στήλες από το CSV: {missing_cols}")

    # 4. Data Cleaning & Type Casting
    
    # Μετατροπή ημερομηνίας σε datetime object
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Καθαρισμός Ticker: Αφαίρεση κενών και μετατροπή σε κεφαλαία
    df['Ticker'] = df['Ticker'].astype(str).str.strip().str.upper()
    
    # Καθαρισμός Action (Buy/Sell): Αφαίρεση κενών και μετατροπή σε κεφαλαία
    df['Action'] = df['Action'].astype(str).str.strip().str.upper()
    
    # Αριθμητικές στήλες: Μετατροπή σε float και χειρισμός μη έγκυρων τιμών
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    
    # Αν τα Fees είναι κενά (NaN), τα κάνουμε 0.0 αντί να πετάξουμε τη γραμμή
    df['Fees'] = pd.to_numeric(df['Fees'], errors='coerce').fillna(0.0)

    # 5. Validation: Αφαίρεση γραμμών με κρίσιμα κενά (π.χ. χωρίς τιμή, ποσότητα ή ημερομηνία)
    initial_rows = len(df)
    df = df.dropna(subset=['Date', 'Ticker', 'Action', 'Quantity', 'Price'])
    dropped_rows = initial_rows - len(df)
    if dropped_rows > 0:
        logging.warning(f"Αφαιρέθηκαν {dropped_rows} γραμμές λόγω ελλιπών βασικών δεδομένων (NaNs).")

    # 6. Ταξινόμηση χρονολογικά (Κρίσιμο για τον αλγόριθμο FIFO)
    df = df.sort_values(by=['Ticker', 'Date']).reset_index(drop=True)

    return df


# --- Block δοκιμής (Εκτελείται μόνο αν τρέξεις απευθείας το αρχείο από το terminal) ---
if __name__ == "__main__":
    # Προσπαθούμε να βρούμε το αρχείο είτε τρέχουμε από το root είτε από τον φάκελο backend
    test_filepath = "../../data/raw/transactions.csv" 
    if not os.path.exists(test_filepath):
        test_filepath = "data/raw/transactions.csv"
        
    try:
        clean_df = load_transactions(test_filepath)
        print("✅ Το αρχείο φορτώθηκε και καθαρίστηκε επιτυχώς!\n")
        print(clean_df.info())
        print("\n--- Προεπισκόπηση Δεδομένων ---")
        print(clean_df)
    except Exception as e:
        print(f"❌ Σφάλμα: {e}")