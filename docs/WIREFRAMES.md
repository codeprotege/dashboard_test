# Wireframes (Text-Based Descriptions)

This document provides text-based descriptions of the key screen layouts for the Financial Dashboard.

## 1. Login / Registration Page (`pages/01_Login.py`)

```
+------------------------------------------------------+
|             Financial Dashboard                      |
|             [ LOGIN / REGISTER ]                     |
+------------------------------------------------------+
|                                                      |
|        [ Tab: Login ]  [ Tab: Register ]             |
|                                                      |
|        +----------------------------------------+    |
|        |         Login to your Account          |    |
|        |                                        |    |
|        |  Username: [________________________]  |    |
|        |  Password: [________________________]  |    |
|        |                                        |    |
|        |              [ Login Button ]          |    |
|        +----------------------------------------+    |
|                                                      |
|        (If Register Tab is active)                   |
|        +----------------------------------------+    |
|        |       Create a New Account             |    |
|        |                                        |    |
|        |  Username: [________________________]  |    |
|        |  Email:    [________________________]  |    |
|        |  Password: [________________________]  |    |
|        |  Confirm:  [________________________]  |    |
|        |                                        |    |
|        |            [ Register Button ]         |    |
|        +----------------------------------------+    |
|                                                      |
|                  [ Back to Home ]                    |
+------------------------------------------------------+
```

## 2. Main Application Layout (Wrapper for all pages)

```
+----------------------+--------------------------------------------------------------------------+
| [S] Financial Dash   | [Main Title of Current Page, e.g., 📈 Interactive Financial Dashboard]    |
| [I]------------------|                                                                          |
| [D] Connection:      |                                                                          |
| [E] [Status Indicator] |                                                                          |
| [B]------------------|                                                                          |
| [A] User Account:    |                                                                          |
| [R] [Login/Logout]   |                                                                          |
| [ ] [Username if logged in] |                                                                  |
| [ ]------------------|                                                                          |
| [ ] Navigation:      |                                                                          |
| [ ] - 🏠 Home        |                                                                          |
| [ ] - 🔑 Login/Reg   |                   [ PAGE CONTENT AREA ]                                    |
| [ ] - 📊 Stock Analysis|                                                                          |
| [ ] - 💹 Forex Monitor|                                                                          |
| [ ] - ⚙️ User Profile|                                                                          |
| [ ] - 🧪 WS Test     |                                                                          |
|                      |                                                                          |
|                      |                                                                          |
+----------------------+--------------------------------------------------------------------------+
```

## 3. Home Page (`app.py` - Content Area)

```
+--------------------------------------------------------------------------+
|             Welcome to Your Financial Dashboard!                         |
|             [Introductory Text & Feature Overview]                       |
|                                                                          |
|             +--------------------------------------------------------+   |
|             | Sample Time Series Plot (Plotly Line Chart)            |   |
|             | [----------------------------------------------------] |   |
|             | [ Chart Area                                         ] |   |
|             | [                                                    ] |   |
|             | [----------------------------------------------------] |   |
|             +--------------------------------------------------------+   |
|                                                                          |
|             [Info: Select a feature from the sidebar...]                 |
+--------------------------------------------------------------------------+
```

## 4. Stock Analysis Page (`pages/02_Stock_Analysis.py` - Content Area)

```
+--------------------------------------------------------------------------+
| [IF SUPERUSER:]                                                          |
| > Admin: Fetch New Stock Data from Alpha Vantage [Expander]              |
|   +--------------------------------------------------------------------+ |
|   | Fetch Symbol: [_________] Output: [Compact/Full] [Refresh] [Fetch] | |
|   | ---                                                                | |
|   | Delete Symbol: [_________] Source: [_________] [Delete Data]       | |
|   +--------------------------------------------------------------------+ |
| [END IF SUPERUSER]                                                       |
|                                                                          |
| Stock Price Analysis                                                     |
| Symbol: [AAPL________] Start: [Date Picker] End: [Date Picker] [Load Data]|
|                                                                          |
| +----------------------------------------------------------------------+ |
| | Price Chart for [SYMBOL] (Plotly Candlestick Chart)                  | |
| | [------------------------------------------------------------------] | |
| | [ Chart Area with Candlestick & Volume Bars (optional)             ] | |
| | [ Rangeslider                                                      ] | |
| | [------------------------------------------------------------------] | |
| +----------------------------------------------------------------------+ |
|                                                                          |
| > View Raw Data Table [Expander]                                         |
|   +--------------------------------------------------------------------+ |
|   | [DataFrame Table: Date, Open, High, Low, Close, Volume, Source]    | |
|   +--------------------------------------------------------------------+ |
|                                                                          |
| Technical Indicators (Placeholder)                                       |
| - RSI: ...                                                               |
| - MACD: ...                                                              |
+--------------------------------------------------------------------------+
```

## 5. User Profile Page (`pages/04_User_Profile.py` - Content Area)

```
+--------------------------------------------------------------------------+
| Your Account Details                                                     |
| Username: [Username]                                                     |
| Email:    [Email]                                                        |
| User ID:  [ID]                                                           |
| ... etc.                                                                 |
| --- (Divider) ---                                                        |
| Update Profile Information                                               |
| [Form: New Username, New Email, Save Changes Button]                     |
| --- (Divider) ---                                                        |
| Change Password                                                          |
| [Form: Old Pass, New Pass, Confirm New Pass, Change Password Button]     |
+--------------------------------------------------------------------------+
```

## 6. Forex Monitor Page (`pages/03_Forex_Monitor.py` - Content Area) - Placeholder

```
+--------------------------------------------------------------------------+
| Forex Exchange Rate Monitor                                              |
| Welcome, [User]!                                                         |
| [Info text about features to be implemented]                             |
|                                                                          |
| Select Currency Pair: [Dropdown: EUR/USD, USD/JPY, ...]                  |
|                                                                          |
| Displaying data for: [SELECTED PAIR]                                     |
| +----------------------------------------------------------------------+ |
| | Exchange Rate for [PAIR] (Placeholder Line Chart)                    | |
| | [------------------------------------------------------------------] | |
| | [ Chart Area                                                       ] | |
| | [------------------------------------------------------------------] | |
| +----------------------------------------------------------------------+ |
|                                                                          |
| Arbitrage Opportunities (Placeholder)                                    |
| [Text: Checking for opportunities...]                                    |
+--------------------------------------------------------------------------+
```

## 7. WebSocket Test Page (`pages/05_WebSocket_Test.py` - Content Area)

```
+--------------------------------------------------------------------------+
| WebSocket Test Page                                                      |
|                                                                          |
| Client ID: [____________] (Defaults to username/test_client)             |
|                                                                          |
| [ Connect to WebSocket Example Button ]                                  |
|                                                                          |
| Send a message: [_________________________________] [ Send Button ]      |
|                                                                          |
| WebSocket Messages:                                                      |
| [Message Log Area - Newest First]                                        |
| Text: Server: ...                                                        |
| Text: You (client_id): ...                                               |
| Text: System: Connected...                                               |
| ...                                                                      |
+--------------------------------------------------------------------------+
```
