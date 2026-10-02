import streamlit as st
import pandas as pd
import plotly.express as px


from src.ui.streamlit.utils import verify_data_availability, create_portfolio_dropdown, style_pnl, HOMEPAGE, TRANSACTION, LOT


st.title("Asset View 📊")

verify_data_availability(st.session_state)

asset_df = st.session_state["asset_df"]

selected_portfolio = create_portfolio_dropdown()

filtered_df = asset_df[asset_df["Portfolio"] == selected_portfolio]

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Portfolio Distribution")
    fig_pie = px.pie(
        filtered_df, 
        values="Current Market Value", 
        names="Ticker",
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("Total Return(%) per Asset")
    fig_bar = px.bar(
        filtered_df, 
        x="Total Return %", 
        y="Ticker", 
        orientation="h",
        color="Total Return %",
        color_continuous_scale=["red", "green"]
    )
    fig_bar.update_layout(yaxis={"categoryorder":"total ascending"}) 
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

col_btn1, col_btn2 = st.columns([1, 3]) 
with col_btn1:
    if st.button("📝 Transaction View"):
        st.session_state["selected_portfolio"] = selected_portfolio
        st.session_state["selected_asset"] = "All" 
        st.switch_page(TRANSACTION)


st.subheader("Asset Analytical Table")
st.write("💡 Choose an Asset for further analysis:")

styled_df = (filtered_df.style
    .format(precision=3)
    .map(
        style_pnl, 
        subset=["Realized PnL", "Realized PnL %", "Unrealized PnL", "Unrealized PnL %", "Total Return", "Total Return %"]
    )
)

event = st.dataframe(
    styled_df,
    use_container_width=True,
    on_select="rerun",
    selection_mode="single-row"
)

if event.selection.rows:
    selected_index = event.selection.rows[0]
    selected_asset = filtered_df.iloc[selected_index]["Ticker"]
    st.session_state["selected_portfolio"] = selected_portfolio
    st.session_state["selected_asset"] = selected_asset
    st.switch_page(LOT)
