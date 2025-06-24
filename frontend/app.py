import streamlit as st
import requests # Keep for direct ping if necessary, though utils.api_call is preferred
import pandas as pd
import plotly.express as px
import os
# from frontend.utils import api_call # utils.py is now available

st.set_page_config(layout="wide", page_title="Financial Dashboard")

st.title("📈 Interactive Financial Dashboard")

# Determine backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# --- Authentication State (Simplified) ---
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None
# --- End Authentication State ---

with st.sidebar:
    st.header("Connection")
    try:
        # Check root endpoint of backend
        ping_url = f"{BACKEND_URL}/"
        # Using requests directly here for a simple ping, no auth needed.
        response = requests.get(ping_url, timeout=5)
        if response.status_code == 200:
            st.success(f"Connected to Backend API.")
            # st.caption(f"Backend says: {response.json().get('message')}")
        else:
            st.error(f"Backend API error. Status: {response.status_code}")
            st.caption(f"URL: {ping_url}")
    except requests.exceptions.RequestException: # Catches ConnectionError, Timeout, etc.
        st.error(f"Connection Error.")
        st.caption(f"URL: {ping_url}. Is backend running?")

    st.header("User Account")
    if st.session_state.auth_token:
        username = st.session_state.user_info.get("username", "N/A") if st.session_state.user_info else "N/A"
        st.write(f"Logged in as: **{username}**")
        if st.button("Logout", key="logout_button_sidebar"): # Unique key
            st.session_state.auth_token = None
            st.session_state.user_info = None
            st.success("Logged out successfully.")
            st.rerun()
    else:
        st.info("You are not logged in.")
        # Links to login/register pages (will be created in frontend/pages/)
        st.page_link("pages/01_Login.py", label="Login / Register")

    st.divider()
    st.header("Navigation")
    st.page_link("app.py", label="🏠 Home", icon="🏠")
    # Use icons for better visual cues if desired
    st.page_link("pages/01_Login.py", label="🔑 Login/Register", icon="🔑")
    st.page_link("pages/02_Stock_Analysis.py", label="📊 Stock Analysis", icon="📊")
    st.page_link("pages/03_Forex_Monitor.py", label="💹 Forex Monitor", icon="💹")
    st.page_link("pages/04_User_Profile.py", label="⚙️ User Profile", icon="⚙️")
    st.page_link("pages/05_WebSocket_Test.py", label="🧪 WS Test", icon="🧪")


st.header("Welcome to Your Financial Dashboard!")
st.markdown("""
This application is designed to help you track financial markets, analyze historical data, and gain insights for your investment decisions.

**Current Features (Placeholders/Basic):**
-   Connection status to the backend API.
-   Basic user login/logout state management.
-   A sample chart below.

**Upcoming Features:**
-   Interactive stock charts (Candlestick, Line, Volume).
-   Technical indicators (RSI, MACD, Moving Averages).
-   Currency exchange rate tracking and visualization.
-   Data uploading and integration with financial APIs.
-   Forecasting tools.
-   Customizable dashboard and user preferences.
""")

# Example Plotly chart
st.subheader("Sample Time Series Plot")
sample_dates = pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05", "2023-01-06"])
sample_values = [100, 102, 99, 101, 105, 103]
sample_df = pd.DataFrame({"Date": sample_dates, "Price": sample_values})
fig = px.line(sample_df, x="Date", y="Price", title="Sample Stock Price Trend", markers=True)
fig.update_layout(xaxis_title="Date", yaxis_title="Price (USD)")
st.plotly_chart(fig, use_container_width=True)

st.info("Select a feature from the sidebar to explore more specific tools and visualizations.")
