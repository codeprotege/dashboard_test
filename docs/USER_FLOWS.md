# User Interaction Flow Diagrams (Text-Based Descriptions)

This document outlines key user interaction flows within the Financial Dashboard application.

## 1. User Registration Flow

```
User (Unauthenticated)
  |
  v
1. Navigates to "Login / Register" page (e.g., via sidebar link or if landing there).
  |
  v
2. Selects "Register" tab.
  |
  v
3. Fills in Registration Form:
   - Username
   - Email
   - Password
   - Confirm Password
  |
  v
4. Clicks "Register" button.
  |
  v
5. Frontend: Performs basic validation (passwords match, fields not empty, length checks).
   |--> (If Validation Fails) --> Shows error message on form. (END)
   |
   v (If Validation Passes)
6. Frontend (utils.api_call): Sends POST request to `/users/` endpoint with registration data.
  |
  v
7. Backend (`users_router.create_user_endpoint`):
   - Validates data (Pydantic schemas: `UserCreate`).
   - Checks for duplicate username/email in database (`crud.get_user_by_username`, `crud.get_user_by_email`).
     |--> (If Duplicate/Validation Fails) --> Returns HTTP 400/422 error with details.
     |
     v (If Checks Pass)
   - Hashes password (`auth.get_password_hash`).
   - Creates new user in database (`crud.create_user`).
   - Returns new user data (as `schemas.UserPublic`) with HTTP 201.
  |
  v
8. Frontend (utils.api_call): Receives response.
   |--> (If Error Response) --> Displays error message (e.g., "Username already taken"). (END)
   |
   v (If Success Response - 201)
9. Frontend: Displays success message (e.g., "Registration successful! You can now log in."). (END)
```

## 2. User Login Flow

```
User (Unauthenticated)
  |
  v
1. Navigates to "Login / Register" page.
  |
  v
2. Selects "Login" tab (usually default).
  |
  v
3. Fills in Login Form:
   - Username
   - Password
  |
  v
4. Clicks "Login" button.
  |
  v
5. Frontend: Sends POST request (form data) to `/auth/token` endpoint.
  |
  v
6. Backend (`auth_router.login_for_access_token`):
   - Authenticates user against database (`auth.authenticate_user` - checks username, verifies password).
     |--> (If Auth Fails or User Inactive) --> Returns HTTP 400/401 error.
     |
     v (If Auth Success)
   - Creates JWT access token (`auth.create_access_token`).
   - Returns token (`schemas.Token`).
  |
  v
7. Frontend: Receives response.
   |--> (If Error Response) --> Displays error message (e.g., "Incorrect username or password"). (END)
   |
   v (If Success Response - Token Received)
8. Frontend: Stores `access_token` in `st.session_state.auth_token`.
  |
  v
9. Frontend (utils.api_call): Sends GET request to `/users/me` with the new token.
  |
  v
10. Backend (`users_router.read_users_me`):
    - Validates token (`auth.get_current_active_user`).
    - Returns current user details (`schemas.UserPublic`).
  |
  v
11. Frontend: Receives user details.
    |--> (If Error) --> Clears token, shows error. (END)
    |
    v (If Success)
12. Frontend: Stores user info in `st.session_state.user_info`.
   |
   v
13. Frontend: Displays success message, updates UI (e.g., shows username in sidebar, enables protected pages).
   User may navigate to dashboard or other pages. (END)
```

## 3. User Password Change Flow

```
User (Authenticated)
  |
  v
1. Navigates to "User Profile" page.
  |
  v
2. Scrolls to "Change Password" section.
  |
  v
3. Fills in Change Password Form:
   - Current Password
   - New Password
   - Confirm New Password
  |
  v
4. Clicks "Change Password" button.
  |
  v
5. Frontend: Performs basic validation (passwords match, fields not empty, new pass length, new!=old).
   |--> (If Validation Fails) --> Shows error message on form. (END)
   |
   v (If Validation Passes)
6. Frontend (utils.api_call): Sends POST request to `/users/me/change-password` with old/new password data and auth token.
  |
  v
7. Backend (`users_router.change_current_user_password`):
   - Gets current authenticated user (`auth.get_current_active_user`).
   - Verifies `old_password` against stored hash (`auth.verify_password`).
     |--> (If Old Password Incorrect) --> Returns HTTP 400 error.
     |
     v (If Old Password Correct)
   - Validates `new_password` (e.g., not same as old - already done by endpoint).
   - Updates user's hashed password in database (`crud.update_password`).
   - Returns success message.
  |
  v
8. Frontend (utils.api_call): Receives response.
   |--> (If Error Response) --> Displays error message (e.g., "Incorrect old password"). (END)
   |
   v (If Success Response)
9. Frontend: Displays success message (e.g., "Password changed successfully!"). (END)
```

## 4. Stock Data Viewing Flow

```
User (Authenticated)
  |
  v
1. Navigates to "Stock Analysis" page.
  |
  v
2. Enters Stock Symbol (e.g., "MSFT").
  |
  v
3. Optionally adjusts Start Date and End Date.
  |
  v
4. Clicks "Load Stock Data" button.
  |
  v
5. Frontend: Clears previous data/error states from `st.session_state`. Validates date range.
   |--> (If Date Range Invalid) --> Shows error. (END)
   |
   v (If Date Range Valid)
6. Frontend (utils.api_call): Sends GET request to `/stocks/{symbol}` endpoint with date range and limit as query parameters, including auth token.
  |
  v
7. Backend (`stocks_router.get_stock_prices`):
   - Retrieves stock price data from database for the symbol and date range (`crud.get_stock_prices_by_symbol`).
   - Returns list of `StockPricePublic` objects (or empty list if no data).
  |
  v
8. Frontend (utils.api_call): Receives response.
   |--> (If Error Response from API call) --> Displays error message. `st.session_state.stock_error` set. (END)
   |
   v (If Success Response - list of stock data)
9. Frontend:
   - If list is empty: Shows warning "No stock data found...". `st.session_state.stock_error` set.
   - If list has data:
     - Converts data to Pandas DataFrame.
     - Sorts by date.
     - Stores DataFrame in `st.session_state.stock_data_df`.
     - Displays success message.
  |
  v
10. Frontend (on rerun due to state change):
    - If `st.session_state.stock_data_df` exists and is not None:
      - Displays Plotly Candlestick chart using the DataFrame.
      - Provides an expander to view the raw data in a table.
    - (Placeholders for Technical Indicators are shown). (END)
```

## 5. Admin: Fetching Stock Data Flow

```
User (Authenticated Superuser)
  |
  v
1. Navigates to "Stock Analysis" page.
  |
  v
2. Opens "Admin: Fetch New Stock Data from Alpha Vantage" expander.
  |
  v
3. Fills in Fetch Data Form:
   - Stock Symbol to Fetch (e.g., "IBM")
   - Output Size (compact/full)
   - Refresh data (checkbox)
  |
  v
4. Clicks "Fetch and Store Data" button.
  |
  v
5. Frontend (utils.api_call): Sends POST request to `/stocks/fetch/{symbol}` endpoint with `output_size` and `refresh_data` as query parameters, including superuser auth token.
  |
  v
6. Backend (`stocks_router.fetch_and_store_stock_data`):
   - Calls `alpha_vantage_service.get_daily_adjusted_stock_data` for the symbol.
     |--> (If Alpha Vantage service raises HTTPException for API errors/limits) --> Re-raises HTTPException.
     |
     v (If AV data fetched successfully)
   - If `refresh_data` is true, calls `crud.delete_stock_prices_by_symbol_and_source` for "AlphaVantage".
   - Calls `crud.create_stock_prices_bulk` to store fetched data.
     |--> (If DB error) --> Returns HTTP 500 error.
     |
     v (If data stored successfully)
   - Returns success message with count of stored items.
  |
  v
7. Frontend (utils.api_call): Receives response.
   |--> (If Error Response) --> Displays error message (e.g., from AV or DB). (END)
   |
   v (If Success Response)
8. Frontend: Displays success message (e.g., "Successfully fetched and stored X data points..."). (END)
```

## 6. Admin: Deleting Stock Data Flow

```
User (Authenticated Superuser)
  |
  v
1. Navigates to "Stock Analysis" page.
  |
  v
2. Opens "Admin: Fetch New Stock Data from Alpha Vantage" expander.
  |
  v
3. Scrolls to "Delete Stock Data by Source (Admin)" sub-section.
  |
  v
4. Fills in Delete Data Form:
   - Stock Symbol to Delete From
   - Data Source (e.g., "AlphaVantage")
  |
  v
5. Clicks "Delete Data by Source" button.
  |
  v
6. Frontend (utils.api_call): Sends DELETE request to `/stocks/{symbol}?data_source={source}` endpoint, including superuser auth token.
  |
  v
7. Backend (`stocks_router.delete_stock_data`):
   - Calls `crud.delete_stock_prices_by_symbol_and_source`.
   - Returns message indicating number of deleted items or if no items were found.
  |
  v
8. Frontend (utils.api_call): Receives response.
   |--> (If Error Response) --> Displays error message. (END)
   |
   v (If Success Response)
9. Frontend: Displays success/info message from backend (e.g., "Successfully deleted X entries..." or "No stock prices found..."). (END)
```
