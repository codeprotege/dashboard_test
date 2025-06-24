from fastapi.testclient import TestClient
from sqlalchemy.orm import Session # For type hinting
from backend import schemas, models # For type hinting and direct DB checks
import datetime
from unittest.mock import patch # For mocking external services like Alpha Vantage

# --- Test Stock Price Creation (Admin/Superuser) ---
def test_create_single_stock_price(client: TestClient, superuser_auth_headers: dict, db_session: Session):
    payload = {
        "symbol": "TESTSTOCK",
        "date": "2023-10-01",
        "open": 100.0,
        "high": 105.0,
        "low": 99.0,
        "close": 102.5,
        "volume": 10000,
        "data_source": "TestSource"
    }
    response = client.post("/stocks/", headers=superuser_auth_headers, json=payload)
    assert response.status_code == 201, f"Response: {response.text}"
    created_price = response.json()
    assert created_price["symbol"] == payload["symbol"].upper()
    assert created_price["date"] == payload["date"]
    assert created_price["close"] == payload["close"]

    # Verify in DB
    price_in_db = db_session.query(models.StockPrice).filter(models.StockPrice.id == created_price["id"]).first()
    assert price_in_db is not None
    assert price_in_db.symbol == payload["symbol"].upper()

def test_create_single_stock_price_normal_user_forbidden(client: TestClient, auth_token_for_test_user: str):
    headers = {"Authorization": f"Bearer {auth_token_for_test_user}"}
    payload = { "symbol": "CANTADD", "date": "2023-10-01", "open": 1, "high": 2, "low": 1, "close": 2, "volume": 100 }
    response = client.post("/stocks/", headers=headers, json=payload)
    assert response.status_code == 403 # Forbidden, as endpoint requires superuser

def test_create_bulk_stock_prices(client: TestClient, superuser_auth_headers: dict, db_session: Session):
    payload = {
        "prices": [
            {"symbol": "BULK1", "date": "2023-10-01", "open": 10, "high": 11, "low": 9, "close": 10.5, "volume": 1000},
            {"symbol": "bulk2", "date": "2023-10-01", "open": 20, "high": 22, "low": 18, "close": 21, "volume": 2000, "data_source": "BulkSource"}
        ],
        "data_source": "DefaultBulkSource" # Common source if not specified in individual items
    }
    response = client.post("/stocks/bulk", headers=superuser_auth_headers, json=payload)
    assert response.status_code == 201, f"Response: {response.text}"
    created_prices = response.json()
    assert len(created_prices) == 2
    assert created_prices[0]["symbol"] == "BULK1"
    assert created_prices[1]["symbol"] == "BULK2" # Router should uppercase it
    assert created_prices[0]["data_source"] == "DefaultBulkSource"
    assert created_prices[1]["data_source"] == "BulkSource" # Individual overrides common

    # Verify in DB
    count_in_db = db_session.query(models.StockPrice).filter(
        (models.StockPrice.symbol == "BULK1") | (models.StockPrice.symbol == "BULK2")
    ).count()
    assert count_in_db == 2


# --- Test Get Stock Prices ---
def test_get_stock_prices_by_symbol(client: TestClient, superuser_auth_headers: dict, db_session: Session):
    # Setup: Create some data first
    test_data = [
        models.StockPrice(symbol="GETTEST", date=datetime.date(2023,10,1), open=1,high=1,low=1,close=1,volume=100, data_source="S1"),
        models.StockPrice(symbol="GETTEST", date=datetime.date(2023,10,2), open=2,high=2,low=2,close=2,volume=200, data_source="S1"),
        models.StockPrice(symbol="ANOTHER", date=datetime.date(2023,10,1), open=3,high=3,low=3,close=3,volume=300, data_source="S2"),
    ]
    db_session.add_all(test_data)
    db_session.commit()

    response = client.get("/stocks/GETTEST", headers=superuser_auth_headers) # Assuming GET might need auth if sensitive
    assert response.status_code == 200
    prices = response.json()
    assert len(prices) == 2
    assert prices[0]["date"] == "2023-10-02" # Default order is date desc
    assert prices[1]["date"] == "2023-10-01"
    for p in prices:
        assert p["symbol"] == "GETTEST"

def test_get_stock_prices_with_date_filters(client: TestClient, superuser_auth_headers: dict, db_session: Session):
    # Data created in previous test might interfere if db_session isn't cleaning properly.
    # db_session fixture in conftest.py IS cleaning up. So this is fine.
    db_session.add_all([
        models.StockPrice(symbol="DATEFILTER", date=datetime.date(2023,9,30), open=1,high=1,low=1,close=1,volume=100),
        models.StockPrice(symbol="DATEFILTER", date=datetime.date(2023,10,1), open=1,high=1,low=1,close=1,volume=100),
        models.StockPrice(symbol="DATEFILTER", date=datetime.date(2023,10,2), open=2,high=2,low=2,close=2,volume=200),
        models.StockPrice(symbol="DATEFILTER", date=datetime.date(2023,10,3), open=3,high=3,low=3,close=3,volume=300),
    ])
    db_session.commit()

    # Test start_date
    response_start = client.get("/stocks/DATEFILTER?start_date=2023-10-02", headers=superuser_auth_headers)
    assert response_start.status_code == 200
    prices_start = response_start.json()
    assert len(prices_start) == 2 # Oct 2, Oct 3
    assert {p["date"] for p in prices_start} == {"2023-10-02", "2023-10-03"}

    # Test end_date
    response_end = client.get("/stocks/DATEFILTER?end_date=2023-10-01", headers=superuser_auth_headers)
    assert response_end.status_code == 200
    prices_end = response_end.json()
    assert len(prices_end) == 2 # Sep 30, Oct 1
    assert {p["date"] for p in prices_end} == {"2023-09-30", "2023-10-01"}

    # Test start_date and end_date
    response_range = client.get("/stocks/DATEFILTER?start_date=2023-10-01&end_date=2023-10-02", headers=superuser_auth_headers)
    assert response_range.status_code == 200
    prices_range = response_range.json()
    assert len(prices_range) == 2 # Oct 1, Oct 2
    assert {p["date"] for p in prices_range} == {"2023-10-01", "2023-10-02"}

    # Test invalid date range
    response_invalid_range = client.get("/stocks/DATEFILTER?start_date=2023-10-03&end_date=2023-10-01", headers=superuser_auth_headers)
    assert response_invalid_range.status_code == 400
    assert "Start date cannot be after end date" in response_invalid_range.json()["detail"]


def test_get_stock_prices_not_found(client: TestClient, superuser_auth_headers: dict):
    response = client.get("/stocks/NOSUCHSYMBOL", headers=superuser_auth_headers)
    assert response.status_code == 200 # Endpoint returns empty list, not 404
    assert response.json() == []


# --- Test Fetch Stock Data (Alpha Vantage Mocking) ---
@patch("backend.services.financial_data_service.AlphaVantageService.get_daily_adjusted_stock_data")
def test_fetch_and_store_stock_data_success(
    mock_get_daily_data, client: TestClient, superuser_auth_headers: dict, db_session: Session
):
    symbol_to_fetch = "FETCHMOCK"
    # Mock the service method to return some sample data
    mock_av_data = [
        schemas.StockPriceCreate(symbol=symbol_to_fetch, date=datetime.date(2023,10,1), open=1,high=2,low=1,close=2,volume=100, data_source="AlphaVantage"),
        schemas.StockPriceCreate(symbol=symbol_to_fetch, date=datetime.date(2023,10,2), open=2,high=3,low=2,close=3,volume=200, data_source="AlphaVantage")
    ]
    mock_get_daily_data.return_value = mock_av_data

    response = client.post(f"/stocks/fetch/{symbol_to_fetch}?output_size=compact&refresh_data=true", headers=superuser_auth_headers)
    assert response.status_code == 200, f"Response: {response.text}"
    assert f"Successfully fetched and stored 2 data points for symbol {symbol_to_fetch}" in response.json()["message"]

    mock_get_daily_data.assert_called_once_with(symbol=symbol_to_fetch, output_size="compact")

    # Verify data in DB
    prices_in_db = db_session.query(models.StockPrice).filter(models.StockPrice.symbol == symbol_to_fetch).all()
    assert len(prices_in_db) == 2
    assert prices_in_db[0].close == 2 # From first item in mock_av_data (order might vary based on DB insert order)
    assert prices_in_db[1].close == 3

@patch("backend.services.financial_data_service.AlphaVantageService.get_daily_adjusted_stock_data")
def test_fetch_and_store_stock_data_no_data_from_av(
    mock_get_daily_data, client: TestClient, superuser_auth_headers: dict
):
    symbol_to_fetch = "NODATA"
    mock_get_daily_data.return_value = [] # Alpha Vantage returns no data

    response = client.post(f"/stocks/fetch/{symbol_to_fetch}", headers=superuser_auth_headers)
    assert response.status_code == 200
    assert f"No data fetched from Alpha Vantage for symbol {symbol_to_fetch}" in response.json()["message"]

@patch("backend.services.financial_data_service.AlphaVantageService.get_daily_adjusted_stock_data")
def test_fetch_and_store_stock_data_av_http_exception(
    mock_get_daily_data, client: TestClient, superuser_auth_headers: dict
):
    symbol_to_fetch = "AVERROR"
    # Simulate an HTTPException from the service (e.g., API key invalid, AV server error)
    mock_get_daily_data.side_effect = HTTPException(status_code=400, detail="Alpha Vantage API Error: Invalid API Call")

    response = client.post(f"/stocks/fetch/{symbol_to_fetch}", headers=superuser_auth_headers)
    assert response.status_code == 400
    assert "Alpha Vantage API Error: Invalid API Call" in response.json()["detail"]


# --- Test Delete Stock Data ---
def test_delete_stock_data_by_symbol_and_source(client: TestClient, superuser_auth_headers: dict, db_session: Session):
    symbol_to_delete = "DELETEME"
    source_to_delete = "TestSourceToDelete"
    # Add some data to delete
    db_session.add_all([
        models.StockPrice(symbol=symbol_to_delete, date=datetime.date(2023,10,1), open=1,high=1,low=1,close=1,volume=100, data_source=source_to_delete),
        models.StockPrice(symbol=symbol_to_delete, date=datetime.date(2023,10,2), open=2,high=2,low=2,close=2,volume=200, data_source=source_to_delete),
        models.StockPrice(symbol=symbol_to_delete, date=datetime.date(2023,10,1), open=3,high=3,low=3,close=3,volume=300, data_source="AnotherSource"), # Keep this one
    ])
    db_session.commit()

    response = client.delete(f"/stocks/{symbol_to_delete}?data_source={source_to_delete}", headers=superuser_auth_headers)
    assert response.status_code == 200, f"Response: {response.text}"
    assert f"Successfully deleted 2 entries for symbol {symbol_to_delete} from source '{source_to_delete}'" in response.json()["message"]

    # Verify in DB
    remaining_for_symbol = db_session.query(models.StockPrice).filter(models.StockPrice.symbol == symbol_to_delete).all()
    assert len(remaining_for_symbol) == 1
    assert remaining_for_symbol[0].data_source == "AnotherSource"

def test_delete_stock_data_no_match(client: TestClient, superuser_auth_headers: dict):
    response = client.delete("/stocks/NOSYMBOL?data_source=NoSource", headers=superuser_auth_headers)
    assert response.status_code == 200
    assert f"No stock prices found for symbol NOSYMBOL from source 'NoSource' to delete" in response.json()["message"]

def test_delete_stock_data_normal_user_forbidden(client: TestClient, auth_token_for_test_user: str):
    headers = {"Authorization": f"Bearer {auth_token_for_test_user}"}
    response = client.delete("/stocks/ANYTHING?data_source=ANY", headers=headers)
    assert response.status_code == 403 # Forbidden
