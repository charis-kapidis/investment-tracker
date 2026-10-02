import streamlit as st
import pandas as pd


from src.ui.streamlit.utils import verify_data_availability, create_portfolio_dropdown, create_asset_dropdown, create_type_dropdown, create_date_range_dropdown


st.title("Transaction View 📝")

verify_data_availability(st.session_state)

transaction_df = st.session_state["transaction_df"]

if "Transaction Date" in transaction_df.columns:
    transaction_df["Transaction Date"] = pd.to_datetime(transaction_df["Transaction Date"])

st.subheader("Filters")

# --- Δημιουργία Φίλτρων σε Στήλες ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    selected_portfolio = create_portfolio_dropdown(transaction=True)
    st.session_state["selected_portfolio"] = selected_portfolio

with col2:
    selected_asset = create_asset_dropdown(transaction=True)
    st.session_state["selected_asset"] = selected_asset

with col3:
    selected_type = create_type_dropdown(transaction=True)
    st.session_state["selected_type"] = selected_type

with col4:
    selected_date_range = create_date_range_dropdown(transaction=True)
    st.session_state["selected_date_range"] = selected_date_range

filtered_df = transaction_df.copy()

if selected_portfolio != "All":
    filtered_df = filtered_df[filtered_df["Portfolio"] == selected_portfolio]

if selected_asset != "All":
    filtered_df = filtered_df[filtered_df["Ticker"] == selected_asset]

if selected_type != "All":
    filtered_df = filtered_df[filtered_df["Transaction Type"] == selected_type]

if len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
    filtered_df = filtered_df[
        (filtered_df["Transaction Date"].dt.date >= start_date) & 
        (filtered_df["Transaction Date"].dt.date <= end_date)
    ]
else:
    raise ValueError("Invalid dates selected")

st.divider()

st.write(f"**{len(filtered_df)}** transactions found")

st.dataframe(
    filtered_df.style.format(precision=3),
    use_container_width=True,
    hide_index=True
)
