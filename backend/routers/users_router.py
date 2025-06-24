from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Annotated

from backend import schemas, crud, models, auth
from backend.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.UserPublic, status_code=status.HTTP_201_CREATED, summary="Create New User")
def create_user_endpoint(
    user_in: schemas.UserCreate,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Create a new user. Username and email must be unique.
    """
    db_user_by_email = crud.get_user_by_email(db, email=user_in.email)
    if db_user_by_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Email '{user_in.email}' already registered.")

    db_user_by_username = crud.get_user_by_username(db, username=user_in.username)
    if db_user_by_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Username '{user_in.username}' already taken.")

    return crud.create_user(db=db, user_in=user_in)

@router.get("/me", response_model=schemas.UserPublic, summary="Get Current User Details")
async def read_users_me(
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)]
):
    """
    Get details for the currently authenticated user.
    """
    return current_user

# Example of a protected route that requires superuser
@router.get("/",
            response_model=List[schemas.UserPublic],
            dependencies=[Depends(auth.get_current_active_superuser)],
            summary="List Users (Superuser only)")
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Retrieve a list of users. Requires superuser privileges.
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=schemas.UserPublic, summary="Get User by ID")
def read_user_by_id(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)]
):
    """
    Retrieve a specific user by their ID.
    Requires superuser privileges, or the current user must be the one being requested.
    """
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=schemas.UserPublic, summary="Update User")
def update_user_endpoint(
    user_id: int,
    user_in: schemas.UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)]
):
    """
    Update a user's details.
    Requires superuser privileges, or the current user must be the one being updated.
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions to update this user")

    # Check for username/email conflicts if they are being changed
    if user_in.username and user_in.username != db_user.username:
        existing_user = crud.get_user_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    if user_in.email and user_in.email != db_user.email:
        existing_user = crud.get_user_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    return crud.update_user(db=db, db_user=db_user, user_in=user_in)

@router.post("/me/change-password", response_model=schemas.Message, summary="Change Current User's Password")
def change_current_user_password(
    password_update: schemas.PasswordUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)]
):
    """
    Change the password for the currently authenticated user.
    """
    if not auth.verify_password(password_update.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password")

    if password_update.old_password == password_update.new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password cannot be the same as the old password")

    crud.update_password(db=db, db_user=current_user, new_password=password_update.new_password)
    return schemas.Message(message="Password updated successfully")
