import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

# Import your FastAPI app and database models/setup
from backend.main import app  # Your FastAPI application
from backend.database import Base, get_db
from backend.models import User # To help with setup/teardown if needed

# --- Test Database Setup ---
# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL_TEST = "sqlite:///./test_db.db" # Or "sqlite:///:memory:" for true in-memory

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL_TEST,
    connect_args={"check_same_thread": False} # Needed for SQLite
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

# Override the get_db dependency for testing
def override_get_db() -> Generator:
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Apply the override for the test session
app.dependency_overrides[get_db] = override_get_db

# --- Pytest Fixtures ---

@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    # Create database tables before tests run
    Base.metadata.create_all(bind=engine_test)
    yield
    # Drop database tables after tests run (optional, if you want a clean slate each full run)
    # Base.metadata.drop_all(bind=engine_test)
    # Or simply delete the test_db.db file if not in-memory
    import os
    if os.path.exists("./test_db.db"):
        os.remove("./test_db.db")

@pytest.fixture(scope="function") # "function" scope for client to ensure clean state per test if needed
def client(create_test_database) -> Generator[TestClient, None, None]:
    """
    Create a new FastAPI TestClient that uses the override_get_db fixture to return
    a database session.
    """
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function")
def db_session(create_test_database) -> Generator[Session, None, None]:
    """
    Yield a database session for direct data manipulation in tests.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        # Clean up data from tables after each test function using this fixture
        # This ensures test isolation.
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
        db.close()

# --- Helper Fixtures for Auth ---

@pytest.fixture(scope="function")
def test_user_data() -> dict:
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword123"
    }

@pytest.fixture(scope="function")
def created_test_user(client: TestClient, test_user_data: dict) -> dict:
    """Creates a user via API and returns the user data including ID."""
    response = client.post("/users/", json=test_user_data)
    assert response.status_code == 201, f"Failed to create user: {response.text}"
    user_info = response.json()
    # Add password to this dict for login convenience in other tests
    user_info["password"] = test_user_data["password"]
    return user_info

@pytest.fixture(scope="function")
def auth_token_for_test_user(client: TestClient, created_test_user: dict) -> str:
    """Logs in the created_test_user and returns the auth token."""
    login_data = {
        "username": created_test_user["username"],
        "password": created_test_user["password"] # Password stored by created_test_user fixture
    }
    response = client.post("/auth/token", data=login_data) # data for form-encoded
    assert response.status_code == 200, f"Failed to login user: {response.text}"
    token_info = response.json()
    return token_info["access_token"]

@pytest.fixture(scope="function")
def superuser_auth_headers(client: TestClient, db_session: Session) -> dict:
    """
    Creates a superuser, logs them in, and returns auth headers.
    Assumes a way to make a user a superuser, e.g., by direct DB manipulation or a specific endpoint.
    For simplicity, we'll create a regular user and then update them in DB to be a superuser.
    """
    superuser_data = {
        "username": "supertestuser",
        "email": "super@example.com",
        "password": "superpassword123"
    }
    # Create user via API
    response = client.post("/users/", json=superuser_data)
    assert response.status_code == 201
    created_user_info = response.json()

    # Make the user a superuser in the DB
    user_in_db = db_session.query(User).filter(User.id == created_user_info["id"]).first()
    assert user_in_db is not None
    user_in_db.is_superuser = True
    db_session.commit()
    db_session.refresh(user_in_db)

    # Log in as superuser
    login_data = {
        "username": superuser_data["username"],
        "password": superuser_data["password"]
    }
    response = client.post("/auth/token", data=login_data)
    assert response.status_code == 200
    token_info = response.json()

    return {"Authorization": f"Bearer {token_info['access_token']}"}
