# Financial Dashboard - User Guide

Welcome to the Financial Dashboard! This guide will help you understand how to use its features.

## 1. Getting Started

### 1.1. Registration
- Navigate to the "Login / Register" page from the sidebar.
- Select the "Register" tab.
- Fill in your desired username (min 3 characters), a valid email address, and a password (min 8 characters).
- Confirm your password.
- Click the "Register" button.
- If successful, you will see a confirmation message. You can then proceed to log in.

### 1.2. Login
- Navigate to the "Login / Register" page.
- Select the "Login" tab.
- Enter your registered username and password.
- Click the "Login" button.
- If successful, you will be logged in, and your username will appear in the sidebar. You will also be able to access protected pages.

### 1.3. Logout
- When logged in, a "Logout" button will appear in the sidebar under "User Account".
- Click this button to securely log out of your session.

## 2. User Profile (`⚙️ User Profile`)

This page allows you to manage your account details.

### 2.1. View Account Details
- Your username, email, user ID, account status (active/inactive), admin status, and join date are displayed.

### 2.2. Update Profile Information
- You can update your username and email address.
- Enter the new details in the respective fields and click "Save Changes".
- Username must be at least 3 characters.
- Email must be a valid format.
- The backend will prevent you from choosing a username or email that is already in use by another account.

### 2.3. Change Password
- To change your password:
    - Enter your current (old) password.
    - Enter your new password (must be at least 8 characters).
    - Confirm your new password.
    - Click "Change Password".
- Your new password cannot be the same as your old password.

## 3. Stock Analysis (`📊 Stock Analysis`)

This page provides tools to analyze stock price data. You must be logged in to access it.

### 3.1. Selecting a Stock and Date Range
- **Enter Stock Symbol:** Type the stock ticker symbol (e.g., AAPL, MSFT) into the input field.
- **Start Date & End Date:** Select the desired date range for the analysis. By default, it shows the last year.
- Click the "Load Stock Data" button.

### 3.2. Viewing Stock Data
- **Candlestick Chart:** A candlestick chart will display the Open, High, Low, and Close (OHLC) prices for the selected symbol and date range. You can zoom and pan this chart. A rangeslider at the bottom allows for quick adjustments to the visible date range on the chart.
- **Raw Data Table:** Below the chart, an expander "View Raw Data Table" allows you to see the fetched data in a tabular format, including date, OHLC prices, volume, and the data source.

### 3.3. Technical Indicators
- (Placeholder Section) This section will display various technical indicators like RSI, MACD, and Moving Averages once implemented.

### 3.4. Admin: Data Management (Visible to Superusers only)
Superusers will see an "Admin: Fetch New Stock Data from Alpha Vantage" expander with the following options:
    - **Fetch New Stock Data:**
        - Enter a stock symbol.
        - Choose "Output Size" ("compact" for last 100 data points, "full" for all available historical data from Alpha Vantage).
        - Check/uncheck "Refresh data" (if checked, any existing data for this symbol from "AlphaVantage" source will be deleted before new data is stored).
        - Click "Fetch and Store Data". The system will contact Alpha Vantage and save the data to the database.
    - **Delete Stock Data by Source:**
        - Enter the stock symbol and the specific data source (e.g., "AlphaVantage", "UserUpload") from which to delete data.
        - Click "Delete Data by Source". This will remove all price entries for that symbol originating from the specified source.

## 4. Forex Monitor (`💹 Forex Monitor`)

(This section will be updated once the Forex monitoring features are implemented.)
- Placeholder for selecting currency pairs.
- Placeholder for displaying exchange rate charts and data.

## 5. WebSocket Test (`🧪 WS Test`)

(This page is for testing basic WebSocket connectivity with the backend.)
- Enter a Client ID (defaults to your username or "test_client").
- Click "Connect to WebSocket Example" to establish the URI.
- Type a message and click "Send Message via WebSocket" to send your message to the example WebSocket endpoint.
- Received messages (including your own echoed back and broadcasts) will appear in the "WebSocket Messages" area.

---
*This user guide will be updated as new features are added to the dashboard.*
