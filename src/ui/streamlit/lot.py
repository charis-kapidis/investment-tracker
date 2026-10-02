import streamlit as st
import pandas as pd


from src.ui.streamlit.utils import verify_data_availability, create_portfolio_dropdown, create_asset_dropdown, style_pnl, TRANSACTION


st.title("Lot View (FIFO) 📦")

verify_data_availability(st.session_state)

lot_df = st.session_state["lot_df"]
asset_df = st.session_state["asset_df"]

col1, col2 = st.columns(2)

with col1:
    selected_portfolio = create_portfolio_dropdown()
    st.session_state["selected_portfolio"] = selected_portfolio

with col2:
    selected_asset = create_asset_dropdown()
    st.session_state["selected_asset"] = selected_asset

st.divider()

st.subheader(f"Summary for: {selected_asset}")

current_asset_data = asset_df[
    (asset_df["Portfolio"] == selected_portfolio) & 
    (asset_df["Ticker"] == selected_asset)
]

if not current_asset_data.empty:
    asset_row = current_asset_data.iloc[0]
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Market Value", 
                f"${asset_row.get('Current Market Value', 0):,.2f}")
    kpi2.metric("Total Cost", 
                f"${asset_row.get('Total Cost', 0):,.2f}")
    kpi3.metric("Unrealized PnL", 
                f"${asset_row.get('Unrealized PnL', 0):,.2f}", 
                f"{asset_row.get('Unrealized PnL %', 0):.2f}%")
    kpi4.metric("Realized PnL", 
                f"${asset_row.get('Realized PnL', 0):,.2f}",
                f"{asset_row.get('Realized PnL %', 0):.2f}%" if pd.notna(asset_row.get("Realized PnL %")) else None)

st.divider()

st.subheader("Lot Analytical Table")

filtered_lot_df = lot_df[
    (lot_df["Portfolio"] == selected_portfolio) & 
    (lot_df["Ticker"] == selected_asset)
]

columns_to_style = [col for col in ["Realized PnL", "Realized PnL %", "Unrealized PnL", "Unrealized PnL %", "Total PnL", "Total ROI %"] if col in filtered_lot_df.columns]

styled_lot_df = (
    filtered_lot_df.style
    .format(precision=3)
    .map(
        style_pnl, 
        subset=columns_to_style
    )
)

event = st.dataframe(
    styled_lot_df,
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row" 
)

if event.selection.rows:
    st.switch_page(TRANSACTION)
