import requests
import datetime
from typing import List, Optional, Dict, Any # Optional, Dict, Any might not be used now but good for future
from fastapi import HTTPException, status

from backend.config import settings
from backend.schemas import StockPriceCreate

ALPHA_VANTAGE_API_URL = "https://www.alphavantage.co/query"

class AlphaVantageService:
    def __init__(self, api_key: Optional[str] = None):
        resolved_api_key = api_key if api_key is not None else settings.ALPHA_VANTAGE_API_KEY
        if not resolved_api_key or resolved_api_key == 'YOUR_API_KEY_HERE_REPLACE_ME':
            # Log this issue, but allow service instantiation for now.
            # The actual error will be raised if a method requiring the key is called.
            print("Warning: Alpha Vantage API key is not configured or is a placeholder.")
            self.api_key = None # Explicitly set to None if invalid/missing
        else:
            self.api_key = resolved_api_key

    def _make_api_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Helper function to make the API request and handle common errors."""
        if not self.api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Alpha Vantage API key is not configured. Cannot fetch data."
            )

        # Add API key to all requests
        params["apikey"] = self.api_key
        params["datatype"] = "json" # Ensure JSON response

        try:
            response = requests.get(ALPHA_VANTAGE_API_URL, params=params, timeout=15) # Added timeout
            response.raise_for_status()
        except requests.exceptions.Timeout:
            print(f"Timeout error fetching data from Alpha Vantage with params: {params.get('symbol')}")
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="Request to Alpha Vantage timed out."
            )
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from Alpha Vantage for {params.get('symbol')}: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error connecting to Alpha Vantage: {str(e)}"
            )

        data = response.json()

        if "Error Message" in data:
            print(f"Alpha Vantage API Error for {params.get('symbol')}: {data['Error Message']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, # Or 404 if symbol not found
                detail=f"Alpha Vantage (symbol: {params.get('symbol')}): {data['Error Message']}"
            )
        if "Note" in data: # Often indicates API limit reached
            print(f"Alpha Vantage API Note for {params.get('symbol')}: {data['Note']}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Alpha Vantage API limit likely reached: {data['Note']}"
            )
        return data

    def get_daily_adjusted_stock_data(self, symbol: str, output_size: str = "compact") -> List[StockPriceCreate]:
        """
        Fetches daily time series data for a stock symbol from Alpha Vantage.
        'output_size' can be 'compact' (last 100) or 'full'.
        """
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol.upper(),
            "outputsize": output_size,
        }

        data = self._make_api_request(params)

        time_series = data.get("Time Series (Daily)")
        if not time_series:
            print(f"No 'Time Series (Daily)' data found for {symbol} in Alpha Vantage response.")
            return []

        stock_prices: List[StockPriceCreate] = []
        for date_str, daily_data in time_series.items():
            try:
                price_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                # Using '4. close' for close price. '5. adjusted close' is also available.
                stock_price = StockPriceCreate(
                    symbol=symbol.upper(), # Ensure symbol is uppercase
                    date=price_date,
                    open=float(daily_data["1. open"]),
                    high=float(daily_data["2. high"]),
                    low=float(daily_data["3. low"]),
                    close=float(daily_data["4. close"]),
                    volume=int(daily_data["6. volume"]),
                    data_source="AlphaVantage"
                )
                # Additional fields like adjusted_close, dividend_amount, split_coefficient are in daily_data
                # e.g., adjusted_close = float(daily_data["5. adjusted close"])
                # These could be added to an extended schema/model if needed.
                stock_prices.append(stock_price)
            except (ValueError, KeyError) as e:
                print(f"Error parsing data for {symbol} on {date_str}: {e}. Data: {daily_data}")
                continue

        return sorted(stock_prices, key=lambda sp: sp.date) # Return sorted by date ascending

# To make this service easily injectable or usable:
alpha_vantage_service = AlphaVantageService()

# Example usage for testing:
# async def main_test():
#     from dotenv import load_dotenv
#     import os
#     # Load .env from project root if running this script directly from backend/services
#     dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
#     load_dotenv(dotenv_path=dotenv_path)
#     print(f"Test API Key from settings: {settings.ALPHA_VANTAGE_API_KEY[:5]}...")
#
#     # Re-initialize with potentially loaded settings if they weren't available at module load time
#     service_test = AlphaVantageService(api_key=settings.ALPHA_VANTAGE_API_KEY)
#
#     try:
#         # stock_data_compact = service_test.get_daily_adjusted_stock_data("IBM")
#         # print(f"\nFetched {len(stock_data_compact)} compact data points for IBM.")
#         # for price in stock_data_compact[:2]:
#         #     print(price.model_dump_json(indent=2))
#
#         stock_data_full = service_test.get_daily_adjusted_stock_data("MSFT", output_size="full")
#         if stock_data_full:
#             print(f"\nFetched {len(stock_data_full)} full data points for MSFT.")
#             # Print first 2 and last 2 (after sorting)
#             print("First 2 entries (oldest):")
#             for price in stock_data_full[:2]:
#                 print(price.model_dump_json(indent=2))
#             print("Last 2 entries (most recent):")
#             for price in stock_data_full[-2:]:
#                 print(price.model_dump_json(indent=2))
#         else:
#             print("No data fetched for MSFT.")
#
#     except HTTPException as e:
#         print(f"HTTP Exception during test: {e.status_code} - {e.detail}")
#     except ValueError as e: # For API key config issues
#         print(f"Configuration Error during test: {e}")
#
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main_test())
