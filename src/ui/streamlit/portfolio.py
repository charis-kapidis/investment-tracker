import streamlit as st
import pandas as pd


from src.ui.streamlit.utils import verify_data_availability, style_pnl, HOMEPAGE, ASSET


st.title("Portfolios View 💼")

verify_data_availability(st.session_state)

portfolio_df = st.session_state["portfolio_df"] 

total_market_value = portfolio_df["Current Market Value"].sum()
total_cost = portfolio_df["Total Cost"].sum()
total_unrealized_pnl = portfolio_df["Unrealized PnL"].sum()
total_unrealized_pct = (total_unrealized_pnl / total_cost * 100) if total_cost > 0 else 0 

col1, col2, col3 = st.columns(3)
col1.metric("Total Market Value", f"${total_market_value:,.2f}")
col2.metric("Total Cost", f"${total_cost:,.2f}")
col3.metric("Total Unrealized PnL", f"${total_unrealized_pnl:,.2f}", f"{total_unrealized_pct:.2f}%")

st.divider()

styled_df = (portfolio_df.style
    .format(precision=3)
    .map(
        style_pnl, 
        subset=["Realized PnL", "Realized PnL %", "Unrealized PnL", "Unrealized PnL %", "Total Return", "Total Return %"]
    )
)

st.subheader("Choose a portfolio for further analysis:")

event = st.dataframe(
    styled_df,
    use_container_width=True,
    on_select="rerun",
    selection_mode="single-row"
)

if event.selection.rows:
    selected_index = event.selection.rows[0]
    selected_portfolio = portfolio_df.iloc[selected_index]["Portfolio"]
    st.session_state["selected_portfolio"] = selected_portfolio
    st.switch_page(ASSET)
