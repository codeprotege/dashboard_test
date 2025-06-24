import streamlit as st

st.set_page_config(page_title="Forex Monitor", layout="wide")
st.title("💹 Forex Exchange Rate Monitor")

if not st.session_state.get("auth_token"):
    st.warning("Please log in to access this page.")
    if st.button("Go to Login"):
        st.switch_page("pages/01_Login.py")
    st.stop()

st.write(f"Welcome, {st.session_state.user_info.get('username', 'user')}!")
st.write("This page will provide tools for monitoring currency exchange rates.")
st.info("Features to be implemented: Major currency pair tracking, real-time (or near real-time) fluctuation visualization, historical data charts, arbitrage opportunity calculation (theoretical).")

# Placeholder for currency pair selection
currency_pairs = ["EUR/USD", "USD/JPY", "GBP/USD", "AUD/USD", "USD/CAD", "USD/CHF"]
selected_pair = st.selectbox("Select Currency Pair", currency_pairs, index=0)

if selected_pair:
    st.write(f"Displaying data for: **{selected_pair}**")
    # TODO: Fetch data for selected_pair from backend API
    # TODO: Display charts and analysis (e.g., line chart for rate, candlestick for daily fluctuation)

    st.subheader(f"Exchange Rate for {selected_pair} (Placeholder)")
    # Replace with actual data and Plotly chart
    import pandas as pd
    import numpy as np
    forex_data = pd.DataFrame({
        'Time': pd.to_datetime(['2023-01-01T10:00', '2023-01-01T10:05', '2023-01-01T10:10', '2023-01-01T10:15']),
        'Rate': [1.0850, 1.0855, 1.0852, 1.0860]
    })
    st.line_chart(forex_data.set_index('Time'))

    st.subheader("Arbitrage Opportunities (Placeholder)")
    st.write("Checking for potential arbitrage opportunities...")
    st.caption("(This is a theoretical feature and depends on available data feeds)")
