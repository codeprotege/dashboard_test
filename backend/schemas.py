from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List # Added List
import datetime

# --- User Schemas ---
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User email address")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="New email address")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="New username")
    is_active: Optional[bool] = Field(None, description="User account active status")
    is_superuser: Optional[bool] = Field(None, description="User superuser status")
    # Password updates should be handled via a separate endpoint/schema for security (e.g., requiring old password)

class UserPublic(UserBase): # Schema for public user information (excluding sensitive data)
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True} # Pydantic V2 (was orm_mode)

# For internal use, like reading from DB, might include hashed_password for auth logic if needed by a specific service
# class UserInDB(UserPublic):
#     hashed_password: str

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer" # Default to bearer, common for JWT

class TokenPayload(BaseModel):
    sub: Optional[str] = Field(None, description="Subject of the token (typically username or user ID)")
    # exp: Optional[datetime.datetime] = None # Expiration time, handled by JWT library

# --- Generic Message Schema ---
class Message(BaseModel):
    message: str

# --- Password Update Schema ---
class PasswordUpdate(BaseModel):
    old_password: str = Field(..., description="User's current password")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")


# --- StockPrice Schemas ---
class StockPriceBase(BaseModel):
    symbol: str = Field(..., description="Stock ticker symbol (e.g., AAPL)")
    date: datetime.date = Field(..., description="Date of the stock price")
    open: float = Field(..., gt=0, description="Opening price")
    high: float = Field(..., gt=0, description="Highest price during the day")
    low: float = Field(..., gt=0, description="Lowest price during the day")
    close: float = Field(..., gt=0, description="Closing price")
    volume: int = Field(..., ge=0, description="Trading volume")
    data_source: Optional[str] = Field(None, description="Source of the data (e.g., AlphaVantage, UserUpload)")

class StockPriceCreate(StockPriceBase):
    pass # For creation, same fields as base for now

class StockPricePublic(StockPriceBase):
    id: int
    created_at: datetime.datetime

    model_config = {"from_attributes": True}

class StockPriceBulkCreate(BaseModel):
    prices: List[StockPriceCreate]
    data_source: Optional[str] = Field(None, description="Common data source for all prices in the bulk load")
