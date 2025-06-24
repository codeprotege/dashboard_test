from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated

from backend import schemas, auth # crud is not directly used here, auth.authenticate_user is
from backend.database import get_db

router = APIRouter()

@router.post("/token", response_model=schemas.Token, summary="Login for Access Token")
async def login_for_access_token(
    db: Annotated[Session, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()] # Standard form data for username/password
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = auth.authenticate_user(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    access_token = auth.create_access_token(
        data={"sub": user.username} # "sub" typically holds the username or user ID
    )
    return {"access_token": access_token, "token_type": "bearer"}
