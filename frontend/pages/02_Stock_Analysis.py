import streamlit as st
import pandas as pd
import plotly.graph_objects as go # For candlestick charts
from frontend.utils import api_call
import datetime

st.set_page_config(page_title="Stock Analysis", layout="wide")
st.title("📊 Stock Analysis")

if not st.session_state.get("auth_token"):
    st.warning("Please log in to access this page.")
    if st.button("Go to Login"):
        st.switch_page("pages/01_Login.py")
    st.stop()

user_info = st.session_state.get("user_info", {}) # Default to empty dict if not found
st.write(f"Welcome, {user_info.get('username', 'user')}!")

# --- Admin Section for Data Fetching ---
if user_info.get("is_superuser"):
    with st.expander("🔑 Admin: Fetch New Stock Data from Alpha Vantage"):
        with st.form("fetch_data_form"):
            fetch_symbol = st.text_input("Stock Symbol to Fetch", placeholder="e.g., MSFT", key="fetch_symbol_input")
            fetch_output_size = st.selectbox("Output Size", ["compact", "full"], index=0, key="fetch_output_size_select")
            fetch_refresh_data = st.checkbox("Refresh data (delete existing before fetching)", value=True, key="fetch_refresh_data_checkbox")
            submit_fetch = st.form_submit_button("Fetch and Store Data")

            if submit_fetch and fetch_symbol:
                params = {
                    "output_size": fetch_output_size,
                    "refresh_data": fetch_refresh_data
                }
                # Endpoint is POST /stocks/fetch/{symbol}
                response = api_call(
                    method="POST",
                    endpoint=f"/stocks/fetch/{fetch_symbol.upper()}",
                    token=st.session_state.auth_token,
                    params=params # Query parameters for output_size and refresh_data
                )
                if response: # api_call returns dict on success, None on error (error already shown by api_call)
                    st.success(response.get("message", "Data fetch process completed."))
            elif submit_fetch and not fetch_symbol:
                st.error("Please enter a stock symbol to fetch.")

        st.markdown("---") # Separator within the expander
        st.subheader("Delete Stock Data by Source (Admin)")
        with st.form("delete_data_form"):
            delete_symbol = st.text_input("Stock Symbol to Delete From", placeholder="e.g., IBM", key="delete_symbol_input")
            delete_source = st.text_input("Data Source", placeholder="e.g., AlphaVantage", value="AlphaVantage", key="delete_source_input")
            submit_delete = st.form_submit_button("Delete Data by Source", type="primary")

            if submit_delete and delete_symbol and delete_source:
                # Confirmation dialog
                # if st.confirm(f"Are you sure you want to delete all data for {delete_symbol.upper()} from source '{delete_source}'? This cannot be undone."):
                response = api_call(
                    method="DELETE",
                    endpoint=f"/stocks/{delete_symbol.upper()}?data_source={delete_source}", # Query param for data_source
                    token=st.session_state.auth_token
                )
                if response:
                    st.success(response.get("message", "Data deletion process completed."))
                # else:
                #     st.error("Failed to initiate data deletion.") # api_call handles specific errors
            elif submit_delete:
                st.error("Please enter both stock symbol and data source to delete.")
    st.divider()


# --- Stock Data Display Section ---
st.header("Stock Price Analysis")

col1, col2, col3 = st.columns([1,1,1])
with col1:
    selected_symbol = st.text_input("Enter Stock Symbol", value=st.session_state.get("selected_stock_symbol", "AAPL"), key="stock_symbol_input")
    if selected_symbol:
        st.session_state.selected_stock_symbol = selected_symbol.upper() # Store for persistence across reruns

with col2:
    # Date range selection
    # Default to last 1 year of data
    today = datetime.date.today()
    default_start_date = today - datetime.timedelta(days=365)
    start_date = st.date_input("Start Date", value=default_start_date, key="stock_start_date")
with col3:
    end_date = st.date_input("End Date", value=today, key="stock_stock_end_date")


if st.button("Load Stock Data", key="load_stock_data_button") and "selected_stock_symbol" in st.session_state:
    symbol_to_load = st.session_state.selected_stock_symbol
    st.session_state.stock_data_df = None # Clear previous data
    st.session_state.stock_error = None

    if start_date > end_date:
        st.error("Error: Start date cannot be after end date.")
        st.session_state.stock_error = "Date range invalid"
    else:
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "limit": 1000 # Max limit for a single fetch, can be adjusted
        }
        stock_data_list = api_call(
            method="GET",
            endpoint=f"/stocks/{symbol_to_load}",
            token=st.session_state.auth_token, # Assuming token might be needed if endpoint becomes protected
            params=params
        )

        if stock_data_list is not None: # api_call returns None on error
            if not stock_data_list: # Empty list means no data found for criteria
                st.warning(f"No stock data found for {symbol_to_load} in the selected date range.")
                st.session_state.stock_error = f"No data for {symbol_to_load}"
            else:
                try:
                    df = pd.DataFrame(stock_data_list)
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.sort_values(by='date') # Ensure data is sorted by date for plotting
                    st.session_state.stock_data_df = df
                    st.success(f"Loaded {len(df)} data points for {symbol_to_load}.")
                except Exception as e:
                    st.error(f"Error processing fetched data: {e}")
                    st.session_state.stock_error = "Data processing error"
        # If stock_data_list is None, api_call already displayed an error.
        # We can set stock_error if needed: else: st.session_state.stock_error = "API fetch error"

# --- Display Chart and Data Table ---
if "stock_data_df" in st.session_state and st.session_state.stock_data_df is not None:
    df_display = st.session_state.stock_data_df
    symbol_loaded = df_display['symbol'].iloc[0] if not df_display.empty else st.session_state.selected_stock_symbol

    st.subheader(f"Price Chart for {symbol_loaded}")

    # Create Candlestick chart
    fig = go.Figure(data=[go.Candlestick(x=df_display['date'],
                                           open=df_display['open'],
                                           high=df_display['high'],
                                           low=df_display['low'],
                                           close=df_display['close'],
                                           name=symbol_loaded)])

    fig.update_layout(
        title=f'{symbol_loaded} Candlestick Chart',
        xaxis_title='Date',
        yaxis_title='Price (USD)', # Assuming USD, make dynamic if needed
        xaxis_rangeslider_visible=True, # Adds a rangeslider
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("View Raw Data Table"):
        # Display selected columns, format date
        display_df_subset = df_display[['date', 'open', 'high', 'low', 'close', 'volume', 'data_source']].copy()
        display_df_subset['date'] = display_df_subset['date'].dt.strftime('%Y-%m-%d')
        st.dataframe(display_df_subset.set_index('date'), use_container_width=True)

elif "stock_error" in st.session_state and st.session_state.stock_error:
    # This message is displayed if there was an error or no data after clicking "Load Stock Data"
    # Specific error/warning messages are shown above by st.error/st.warning
    pass # Error/warning already shown

st.divider()
st.subheader("Technical Indicators (Placeholder)")
st.write("- RSI: To be implemented")
st.write("- MACD: To be implemented")
st.write("- Moving Averages: To be implemented")
