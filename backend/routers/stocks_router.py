from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Annotated, Optional
import datetime

from backend import schemas, crud, models, auth # Assuming auth might be needed for protected routes
from backend.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.StockPricePublic, status_code=status.HTTP_201_CREATED,
             summary="Create Single Stock Price Entry",
             dependencies=[Depends(auth.get_current_active_superuser)]) # Example: Protected
def create_single_stock_price(
    price_in: schemas.StockPriceCreate,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Create a single stock price entry. Requires superuser privileges.
    Ensures symbol is uppercase.
    """
    price_in.symbol = price_in.symbol.upper()
    # Optional: Check if data for this exact symbol and date already exists to prevent duplicates
    # existing_entry = db.query(models.StockPrice).filter(
    #     models.StockPrice.symbol == price_in.symbol,
    #     models.StockPrice.date == price_in.date
    # ).first()
    # if existing_entry:
    #     raise HTTPException(
    #         status_code=status.HTTP_409_CONFLICT,
    #         detail=f"Stock price for {price_in.symbol} on {price_in.date} already exists."
    #     )
    return crud.create_stock_price(db=db, price_in=price_in)

@router.post("/bulk", response_model=List[schemas.StockPricePublic], status_code=status.HTTP_201_CREATED,
              summary="Create Multiple Stock Price Entries (Bulk)",
              dependencies=[Depends(auth.get_current_active_superuser)]) # Example: Protected
def create_bulk_stock_prices(
    prices_in: schemas.StockPriceBulkCreate,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Create multiple stock price entries in bulk. Requires superuser privileges.
    Ensures all symbols are uppercase.
    """
    for price in prices_in.prices:
        price.symbol = price.symbol.upper()
    # Optional: Add more sophisticated duplicate checking for bulk operations if needed.
    return crud.create_stock_prices_bulk(db=db, prices_in=prices_in)

@router.get("/{symbol}", response_model=List[schemas.StockPricePublic],
            summary="Get Stock Prices by Symbol")
def get_stock_prices(
    symbol: str,
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    start_date: Optional[datetime.date] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    # current_user: models.User = Depends(auth.get_current_active_user) # If all stock data access needs auth
):
    """
    Get historical stock prices for a given symbol.
    Supports pagination and date range filtering.
    """
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start date cannot be after end date.")

    prices = crud.get_stock_prices_by_symbol(
        db=db,
        symbol=symbol.upper(),
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date
    )
    if not prices:
        # Distinguish between no data found and symbol not existing if necessary
        # For now, just return empty list, client can interpret.
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No stock prices found for symbol {symbol.upper()}")
        pass
    return prices

@router.delete("/{symbol}", response_model=schemas.Message,
              summary="Delete Stock Prices by Symbol and Source",
              dependencies=[Depends(auth.get_current_active_superuser)]) # Example: Protected
def delete_stock_data(
    symbol: str,
    data_source: str = Query(..., description="Specify the data source to delete (e.g., 'AlphaVantage', 'UserUpload')"),
    db: Annotated[Session, Depends(get_db)],
):
    """
    Delete all stock price entries for a given symbol and data source.
    Requires superuser privileges.
    """
    num_deleted = crud.delete_stock_prices_by_symbol_and_source(db=db, symbol=symbol.upper(), data_source=data_source)
    if num_deleted == 0:
        # This is not necessarily an error, could be that no data matched.
        return schemas.Message(message=f"No stock prices found for symbol {symbol.upper()} from source '{data_source}' to delete.")
    return schemas.Message(message=f"Successfully deleted {num_deleted} entries for symbol {symbol.upper()} from source '{data_source}'.")

# Need to import the service
from backend.services.financial_data_service import alpha_vantage_service

@router.post("/fetch/{symbol}",
             response_model=schemas.Message, # Or List[schemas.StockPricePublic] to return the fetched data
             summary="Fetch and Store Stock Data from Alpha Vantage",
             dependencies=[Depends(auth.get_current_active_superuser)])
def fetch_and_store_stock_data(
    symbol: str,
    db: Annotated[Session, Depends(get_db)],
    output_size: str = Query("compact", enum=["compact", "full"], description="Output size for Alpha Vantage (compact: 100 points, full: all data)"),
    refresh_data: bool = Query(True, description="Delete existing data from AlphaVantage for this symbol before fetching new data.")
):
    """
    Fetches daily adjusted stock data for the given symbol from Alpha Vantage
    and stores it in the database. Requires superuser privileges.
    """
    try:
        fetched_prices_schemes = alpha_vantage_service.get_daily_adjusted_stock_data(
            symbol=symbol.upper(),
            output_size=output_size
        )
    except HTTPException as e:
        # Re-raise if it's an HTTPException from the service (e.g., API key error, AlphaVantage error)
        raise e
    except Exception as e:
        # Catch any other unexpected errors from the service call
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred while fetching data: {str(e)}")

    if not fetched_prices_schemes:
        return schemas.Message(message=f"No data fetched from Alpha Vantage for symbol {symbol.upper()}. Nothing stored.")

    if refresh_data:
        crud.delete_stock_prices_by_symbol_and_source(db=db, symbol=symbol.upper(), data_source="AlphaVantage")

    # Prepare for bulk creation
    bulk_create_input = schemas.StockPriceBulkCreate(
        prices=fetched_prices_schemes,
        # data_source="AlphaVantage" # This is now set within each StockPriceCreate object by the service
    )

    try:
        stored_prices = crud.create_stock_prices_bulk(db=db, prices_in=bulk_create_input)
    except Exception as e:
        # Handle potential DB errors during bulk insert
        # Log e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error storing fetched data: {str(e)}")

    return schemas.Message(message=f"Successfully fetched and stored {len(stored_prices)} data points for symbol {symbol.upper()} from Alpha Vantage.")
