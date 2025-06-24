from fastapi.testclient import TestClient
from sqlalchemy.orm import Session # For type hinting
from backend import schemas, models # For type hinting and direct DB checks if needed

# --- Test User Creation ---
def test_create_user_success(client: TestClient, db_session: Session, test_user_data: dict):
    # db_session fixture will clean up this user afterwards
    response = client.post("/users/", json=test_user_data)
    assert response.status_code == 201, f"Response text: {response.text}"
    created_user = response.json()
    assert created_user["username"] == test_user_data["username"]
    assert created_user["email"] == test_user_data["email"]
    assert "id" in created_user
    assert "hashed_password" not in created_user # Ensure password not returned

    # Verify in DB (optional, but good for confidence)
    user_in_db = db_session.query(models.User).filter(models.User.id == created_user["id"]).first()
    assert user_in_db is not None
    assert user_in_db.username == test_user_data["username"]

def test_create_user_duplicate_username(client: TestClient, created_test_user: dict, test_user_data: dict):
    # created_test_user fixture already created a user with test_user_data["username"]
    duplicate_username_payload = {
        "username": test_user_data["username"], # Same username
        "email": "another_email@example.com",
        "password": "anotherpassword"
    }
    response = client.post("/users/", json=duplicate_username_payload)
    assert response.status_code == 400
    assert f"Username '{test_user_data['username']}' already taken" in response.json()["detail"]

def test_create_user_duplicate_email(client: TestClient, created_test_user: dict, test_user_data: dict):
    duplicate_email_payload = {
        "username": "anotherusername",
        "email": test_user_data["email"], # Same email
        "password": "anotherpassword"
    }
    response = client.post("/users/", json=duplicate_email_payload)
    assert response.status_code == 400
    assert f"Email '{test_user_data['email']}' already registered" in response.json()["detail"]

def test_create_user_invalid_email(client: TestClient, test_user_data: dict):
    invalid_email_payload = test_user_data.copy()
    invalid_email_payload["email"] = "not-an-email"
    response = client.post("/users/", json=invalid_email_payload)
    assert response.status_code == 422 # Pydantic validation error

def test_create_user_short_password(client: TestClient, test_user_data: dict):
    short_password_payload = test_user_data.copy()
    short_password_payload["password"] = "short"
    response = client.post("/users/", json=short_password_payload)
    assert response.status_code == 422 # Pydantic validation error
    assert "ensure this value has at least 8 characters" in response.text


# --- Test Get Users (Superuser) ---
def test_read_users_as_superuser(client: TestClient, superuser_auth_headers: dict, created_test_user: dict):
    # created_test_user and the superuser itself should be in the list
    response = client.get("/users/", headers=superuser_auth_headers)
    assert response.status_code == 200
    users_list = response.json()
    assert isinstance(users_list, list)
    assert len(users_list) >= 2 # At least the superuser and the created_test_user
    usernames_in_response = [u["username"] for u in users_list]
    assert created_test_user["username"] in usernames_in_response
    assert "supertestuser" in usernames_in_response # From superuser_auth_headers fixture

def test_read_users_as_normal_user(client: TestClient, auth_token_for_test_user: str):
    headers = {"Authorization": f"Bearer {auth_token_for_test_user}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 403 # Forbidden
    assert "user does not have enough privileges" in response.json()["detail"]

def test_read_users_unauthenticated(client: TestClient):
    response = client.get("/users/")
    assert response.status_code == 401 # Unauthorized


# --- Test Get User by ID ---
def test_read_user_by_id_as_superuser(client: TestClient, superuser_auth_headers: dict, created_test_user: dict):
    user_id_to_get = created_test_user["id"]
    response = client.get(f"/users/{user_id_to_get}", headers=superuser_auth_headers)
    assert response.status_code == 200
    user = response.json()
    assert user["id"] == user_id_to_get
    assert user["username"] == created_test_user["username"]

def test_read_own_user_by_id_as_normal_user(client: TestClient, auth_token_for_test_user: str, created_test_user: dict):
    user_id_to_get = created_test_user["id"] # This is the authenticated user's ID
    headers = {"Authorization": f"Bearer {auth_token_for_test_user}"}
    response = client.get(f"/users/{user_id_to_get}", headers=headers)
    assert response.status_code == 200
    user = response.json()
    assert user["id"] == user_id_to_get

def test_read_other_user_by_id_as_normal_user(client: TestClient, auth_token_for_test_user: str, superuser_auth_headers: dict, db_session: Session):
    # Get superuser's ID (or any other user's ID that is not the current normal user)
    # The superuser created in superuser_auth_headers is cleaned up by db_session fixture after that fixture's scope
    # So, we need to ensure a "other user" exists during this test.
    # Let's create a fresh "other user".
    other_user_payload = {"username": "otheruser", "email": "other@example.com", "password": "otherpassword"}
    response_create = client.post("/users/", json=other_user_payload) # Unauthenticated creation is fine for test setup
    assert response_create.status_code == 201
    other_user_id = response_create.json()["id"]

    headers_normal_user = {"Authorization": f"Bearer {auth_token_for_test_user}"}
    response = client.get(f"/users/{other_user_id}", headers=headers_normal_user)
    assert response.status_code == 403 # Forbidden for normal user to access other user's details by ID
    assert "Not enough permissions" in response.json()["detail"]

def test_read_user_by_id_not_found(client: TestClient, superuser_auth_headers: dict):
    non_existent_id = 999999
    response = client.get(f"/users/{non_existent_id}", headers=superuser_auth_headers)
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

# --- Test Update User ---
def test_update_own_user_details(client: TestClient, auth_token_for_test_user: str, created_test_user: dict):
    user_id_to_update = created_test_user["id"]
    headers = {"Authorization": f"Bearer {auth_token_for_test_user}"}
    update_payload = {
        "email": "updated_email@example.com",
        "username": "updated_username"
    }
    response = client.put(f"/users/{user_id_to_update}", headers=headers, json=update_payload)
    assert response.status_code == 200, f"Response: {response.text}"
    updated_user = response.json()
    assert updated_user["email"] == update_payload["email"]
    assert updated_user["username"] == update_payload["username"]
    # Ensure original fields not meant to be updated by this payload are still same or default
    assert updated_user["is_active"] == created_test_user.get("is_active", True) # Default is True

def test_update_other_user_as_superuser(client: TestClient, superuser_auth_headers: dict, created_test_user: dict):
    user_id_to_update = created_test_user["id"] # Superuser updates the normal test user
    update_payload = {
        "email": "updated_by_superuser@example.com",
        "is_active": False
    }
    response = client.put(f"/users/{user_id_to_update}", headers=superuser_auth_headers, json=update_payload)
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["email"] == update_payload["email"]
    assert updated_user["is_active"] == False

def test_update_other_user_as_normal_user(client: TestClient, auth_token_for_test_user: str, db_session: Session):
    # Create another user for the normal user to attempt to update
    other_user_payload = {"username": "victimuser", "email": "victim@example.com", "password": "victimpassword"}
    response_create = client.post("/users/", json=other_user_payload)
    assert response_create.status_code == 201
    other_user_id = response_create.json()["id"]

    headers_normal_user = {"Authorization": f"Bearer {auth_token_for_test_user}"}
    update_payload = {"email": "hacked@example.com"}
    response = client.put(f"/users/{other_user_id}", headers=headers_normal_user, json=update_payload)
    assert response.status_code == 403 # Forbidden
    assert "Not enough permissions" in response.json()["detail"]

def test_update_user_username_conflict(client: TestClient, superuser_auth_headers: dict, created_test_user: dict):
    # Create a second user
    second_user_payload = {"username": "seconduser", "email": "second@example.com", "password": "secondpassword"}
    response_create = client.post("/users/", json=second_user_payload, headers=superuser_auth_headers) # Superuser creates
    assert response_create.status_code == 201
    # second_user_id = response_create.json()["id"]

    # Try to update created_test_user to have username 'seconduser'
    user_id_to_update = created_test_user["id"]
    update_payload = {"username": "seconduser"}
    response = client.put(f"/users/{user_id_to_update}", headers=superuser_auth_headers, json=update_payload)
    assert response.status_code == 400
    assert "Username already taken" in response.json()["detail"]

# Note: Deletion of users is not implemented in the current users_router.
# If it were, tests for DELETE /users/{user_id} would be here.
