from datetime import datetime, timedelta, timezone
from typing import Optional, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend import crud, models, schemas # Adjusted import
from backend.config import settings # Adjusted import
from backend.database import get_db # Adjusted import

# --- Password Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# --- JWT Token Creation ---
ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY # Should be a strong, random string
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)}) # Add issued_at time
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- OAuth2 Scheme ---
# The tokenUrl should point to your login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token") # Relative to server root

# --- User Authentication and Authorization Dependencies ---
async def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)]
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub") # "sub" is the standard claim for subject (username)
        if username is None:
            raise credentials_exception
        token_payload = schemas.TokenPayload(sub=username) # Validate payload structure
    except JWTError: # Catches expired signature, invalid signature, etc.
        raise credentials_exception

    user = crud.get_user_by_username(db, username=token_payload.sub)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[models.User, Depends(get_current_user)]
) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

async def get_current_active_superuser(
    current_user: Annotated[models.User, Depends(get_current_active_user)] # Depends on active user
) -> models.User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges (superuser required)"
        )
    return current_user

# --- Authenticate User Function (for login endpoint) ---
def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    """
    Authenticates a user by username and password.
    Returns the user object if authentication is successful, otherwise None.
    """
    user = crud.get_user_by_username(db, username=username)
    if not user:
        return None # User not found
    if not verify_password(password, user.hashed_password):
        return None # Invalid password
    return user # Authentication successful
