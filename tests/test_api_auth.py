from fastapi.testclient import TestClient
from sqlalchemy.orm import Session # For type hinting if using db_session directly
from backend import schemas # For response model validation if needed

# Test user registration (already implicitly tested by created_test_user fixture)

def test_login_for_access_token(client: TestClient, created_test_user: dict):
    login_data = {
        "username": created_test_user["username"],
        "password": created_test_user["password"] # From fixture where password was added
    }
    response = client.post("/auth/token", data=login_data) # Form data
    assert response.status_code == 200
    token = response.json()
    assert "access_token" in token
    assert token["token_type"] == "bearer"

def test_login_inactive_user(client: TestClient, db_session: Session, test_user_data: dict):
    # Create user
    response_create = client.post("/users/", json=test_user_data)
    assert response_create.status_code == 201
    user_id = response_create.json()["id"]

    # Deactivate user directly in DB
    from backend.models import User
    user_in_db = db_session.query(User).filter(User.id == user_id).first()
    assert user_in_db is not None
    user_in_db.is_active = False
    db_session.commit()

    # Attempt login
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    response_login = client.post("/auth/token", data=login_data)
    assert response_login.status_code == 400 # As per auth_router logic for inactive user
    assert response_login.json()["detail"] == "Inactive user"

def test_login_wrong_password(client: TestClient, created_test_user: dict):
    login_data = {
        "username": created_test_user["username"],
        "password": "wrongwrongpassword"
    }
    response = client.post("/auth/token", data=login_data)
    assert response.status_code == 401 # Unauthorized
    assert response.json()["detail"] == "Incorrect username or password"

def test_login_nonexistent_user(client: TestClient):
    login_data = {
        "username": "nonexistentuser123",
        "password": "anypassword"
    }
    response = client.post("/auth/token", data=login_data)
    assert response.status_code == 401 # Unauthorized
    assert response.json()["detail"] == "Incorrect username or password"

# Test /users/me endpoint (part of user routes but heavily auth related)
def test_read_users_me_requires_auth(client: TestClient):
    response = client.get("/users/me")
    assert response.status_code == 401 # Unauthorized without token
    assert response.json()["detail"] == "Not authenticated" # Default from FastAPI for missing token

def test_read_users_me_with_auth(client: TestClient, auth_token_for_test_user: str, created_test_user: dict):
    headers = {"Authorization": f"Bearer {auth_token_for_test_user}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    user_me = response.json()
    assert user_me["username"] == created_test_user["username"]
    assert user_me["email"] == created_test_user["email"]
    assert "password" not in user_me # Ensure password is not returned
    assert "hashed_password" not in user_me

def test_read_users_me_with_invalid_token(client: TestClient):
    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

# Test password change
def test_change_password_success(client: TestClient, auth_token_for_test_user: str, created_test_user: dict):
    headers = {"Authorization": f"Bearer {auth_token_for_test_user}"}
    payload = {
        "old_password": created_test_user["password"],
        "new_password": "newSecurePassword123"
    }
    response = client.post("/users/me/change-password", headers=headers, json=payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"

    # Verify login with new password
    login_data_new_pass = {
        "username": created_test_user["username"],
        "password": "newSecurePassword123"
    }
    response_login_new = client.post("/auth/token", data=login_data_new_pass)
    assert response_login_new.status_code == 200

    # Verify login with old password fails
    login_data_old_pass = {
        "username": created_test_user["username"],
        "password": created_test_user["password"]
    }
    response_login_old = client.post("/auth/token", data=login_data_old_pass)
    assert response_login_old.status_code == 401


def test_change_password_wrong_old_password(client: TestClient, auth_token_for_test_user: str):
    headers = {"Authorization": f"Bearer {auth_token_for_test_user}"}
    payload = {
        "old_password": "thisisnottheoldpassword",
        "new_password": "newSecurePassword123"
    }
    response = client.post("/users/me/change-password", headers=headers, json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect old password"

def test_change_password_new_same_as_old(client: TestClient, auth_token_for_test_user: str, created_test_user: dict):
    headers = {"Authorization": f"Bearer {auth_token_for_test_user}"}
    payload = {
        "old_password": created_test_user["password"],
        "new_password": created_test_user["password"] # Same as old
    }
    response = client.post("/users/me/change-password", headers=headers, json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "New password cannot be the same as the old password"

def test_change_password_new_too_short(client: TestClient, auth_token_for_test_user: str, created_test_user: dict):
    headers = {"Authorization": f"Bearer {auth_token_for_test_user}"}
    payload = {
        "old_password": created_test_user["password"],
        "new_password": "short" # Too short
    }
    response = client.post("/users/me/change-password", headers=headers, json=payload)
    # This validation is done by Pydantic schema `PasswordUpdate`
    assert response.status_code == 422 # Unprocessable Entity for Pydantic validation errors
    # You might want to check the detail more specifically if needed
    # error_detail = response.json()["detail"][0]
    # assert error_detail["loc"] == ["body", "new_password"]
    # assert "at least 8 characters" in error_detail["msg"]
    assert "ensure this value has at least 8 characters" in response.text # Simpler check
