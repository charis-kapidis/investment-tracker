import streamlit as st
import pandas as pd


from src.ui.streamlit.utils import load_data, PORTFOLIO, DEMO_FILENAME, SCHEMA_EXAMPLE


st.title("Welcome to Portfolio Tracker 📈")
st.write("Track & Analyze your investments on multiple granularity levels.")

col_actions, col_info = st.columns([1, 1], gap="large")

with col_actions:
    st.subheader("Data Upload Functionality")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file is not None:
        if st.button("Analyze Data", type="primary"):
            with st.spinner("Calculating metrics..."):
                load_data(uploaded_file)
                st.success("Calculating metrics completed!")
                st.switch_page(PORTFOLIO)
    
    st.divider()

    st.subheader("Data Input Functionality")
    st.info("In a future version, you will be able to input your transactions one by one without using CSV files.")

    st.divider()

    st.subheader("Demo Data Functionality")
    st.write("Don't have transaction data now? Check how the application works with demo data.")
    if st.button("Load demo data"):
        with st.spinner("Loading demo transaction data..."):
            load_data(DEMO_FILENAME)
            st.success("Calculating metrics completed!")
            st.switch_page(PORTFOLIO)

with col_info:
    st.subheader("CSV File Requirements")
    st.write("For the analysis to run smoothly, the CSV file must include **specific columns**. Find an example below:")
    schema_example = SCHEMA_EXAMPLE
    st.dataframe(schema_example, hide_index=True, use_container_width=True)

    st.divider()
    
    empty_template = pd.DataFrame(columns=SCHEMA_EXAMPLE.columns).to_csv(index=False)
    st.write("Download an empty template to fill your transaction data:")
    st.download_button(
        label="📥 Download CSV Template",
        data=empty_template,
        file_name="transaction_template.csv",
        mime="text/csv"
    )
