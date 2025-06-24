from sqlalchemy import Column, Integer, String, Boolean, DateTime # Float, ForeignKey
# from sqlalchemy.orm import relationship # For future relationships
from backend.database import Base # Correct import from the new database.py
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False) # Optional: for admin users
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

# Add other models here as needed:
from sqlalchemy import Float, Date, ForeignKey # Added Float, Date, ForeignKey
# from sqlalchemy.orm import relationship

# Could have a separate Stock model for metadata if needed:
# class Stock(Base):
#     __tablename__ = "stocks"
#     id = Column(Integer, primary_key=True, index=True)
#     symbol = Column(String, unique=True, index=True, nullable=False)
#     company_name = Column(String, nullable=True)
#     exchange = Column(String, nullable=True)
#     # prices = relationship("StockPrice", back_populates="stock_info")


class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    # stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=True) # If using Stock model
    symbol = Column(String, index=True, nullable=False) # For now, symbol directly here
    date = Column(Date, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False) # Integer is fine for volume
    data_source = Column(String, nullable=True) # E.g., 'AlphaVantage', 'UserUpload', 'YahooFinance'

    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))

    # If using Stock model:
    # stock_info = relationship("Stock", back_populates="prices")

    def __repr__(self):
        return f"<StockPrice(symbol='{self.symbol}', date='{self.date}', close={self.close})>"


# class ForexPair(Base): ...
# class UserDataPreference(Base): ...
