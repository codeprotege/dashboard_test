from sqlalchemy.orm import Session
from typing import Optional # Added for type hinting
from backend import models, schemas
from backend.auth import get_password_hash # For hashing password on create/update

# --- User CRUD Operations ---
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user_in.password)
    db_user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password
        # is_active, is_superuser defaults are set in the model
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- StockPrice CRUD Operations ---

def create_stock_price(db: Session, price_in: schemas.StockPriceCreate) -> models.StockPrice:
    db_price = models.StockPrice(**price_in.model_dump())
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price

def create_stock_prices_bulk(db: Session, prices_in: schemas.StockPriceBulkCreate) -> list[models.StockPrice]:
    db_prices = []
    for price_data in prices_in.prices:
        # If a common data_source is provided in StockPriceBulkCreate and not in individual price_data
        if prices_in.data_source and price_data.data_source is None:
            final_price_data = price_data.model_dump()
            final_price_data['data_source'] = prices_in.data_source
            db_price = models.StockPrice(**final_price_data)
        else:
            db_price = models.StockPrice(**price_data.model_dump())
        db.add(db_price)
        db_prices.append(db_price)
    db.commit()
    for db_price in db_prices: # Refresh each object after commit to get DB-generated values like ID
        db.refresh(db_price)
    return db_prices

def get_stock_prices_by_symbol(
    db: Session,
    symbol: str,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime.date] = None, # Use datetime.date from schemas
    end_date: Optional[datetime.date] = None
) -> list[models.StockPrice]:
    query = db.query(models.StockPrice).filter(models.StockPrice.symbol == symbol.upper())
    if start_date:
        query = query.filter(models.StockPrice.date >= start_date)
    if end_date:
        query = query.filter(models.StockPrice.date <= end_date)

    return query.order_by(models.StockPrice.date.desc()).offset(skip).limit(limit).all()

def delete_stock_prices_by_symbol_and_source(db: Session, symbol: str, data_source: str) -> int:
    """
    Deletes stock prices for a given symbol and data source.
    Returns the number of rows deleted.
    """
    num_deleted = db.query(models.StockPrice).filter(
        models.StockPrice.symbol == symbol.upper(),
        models.StockPrice.data_source == data_source
    ).delete(synchronize_session=False) # False is usually fine for bulk deletes
    db.commit()
    return num_deleted

def update_user(db: Session, db_user: models.User, user_in: schemas.UserUpdate) -> models.User:
    update_data = user_in.model_dump(exclude_unset=True) # Pydantic V2

    # If password needs to be updated, it should be handled separately and hashed
    # For now, this UserUpdate schema does not include password change.

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> Optional[models.User]:
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user # Returns the deleted user or None if not found

def update_password(db: Session, db_user: models.User, new_password: str) -> models.User:
    """
    Updates a user's password.
    """
    db_user.hashed_password = get_password_hash(new_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
