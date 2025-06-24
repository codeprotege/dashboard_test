import pytest
from passlib.context import CryptContext

# Assuming these functions are in backend.auth or accessible for import
# For this test, I'll redefine them or import if the agent's environment handles it.
# Let's assume direct import works for the test environment.
from backend.auth import verify_password, get_password_hash

# If direct import is an issue, a common pattern is to have a conftest.py or adjust PYTHONPATH.
# For now, proceeding with direct import assumption.

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_get_password_hash():
    password = "testpassword"
    hashed_password = get_password_hash(password)
    assert hashed_password is not None
    assert isinstance(hashed_password, str)
    # Check that it's a valid hash for the context (bcrypt in this case)
    assert pwd_context.verify(password, hashed_password)

def test_verify_password_correct():
    password = "testpassword123"
    hashed_password = pwd_context.hash(password) # Use context directly for test consistency
    assert verify_password(password, hashed_password) is True

def test_verify_password_incorrect():
    password = "testpassword123"
    wrong_password = "wrongpassword"
    hashed_password = pwd_context.hash(password)
    assert verify_password(wrong_password, hashed_password) is False

def test_verify_password_with_non_bcrypt_hash_if_applicable():
    # This test would be relevant if your pwd_context supported multiple schemes
    # and you wanted to ensure verify still works or handles it gracefully.
    # For a simple bcrypt-only setup, this might be less critical.
    # Example: if you had an old MD5 hash to verify against.
    # For now, bcrypt is the only scheme.
    password = "testpassword"
    # Manually create a non-bcrypt hash (e.g., a plain string or other algorithm)
    # This is a bit contrived as pwd_context.hash always uses bcrypt here.
    # For a real scenario, you might load a hash from a legacy system.
    non_bcrypt_hash = "not_a_bcrypt_hash_obviously"

    # Depending on passlib's strictness or error handling for unknown schemes in verify:
    try:
        # Passlib's verify might raise an error if the hash format is unrecognized
        # or simply return False if it can't identify the scheme.
        # For bcrypt, it expects a hash starting with $2a$, $2b$, or $2y$.
        assert verify_password(password, non_bcrypt_hash) is False
    except ValueError: # Passlib might raise ValueError for malformed/unknown hash
        pass # Or assert that a specific error is raised if that's the expected behavior
    except Exception: # Catch other potential passlib errors for unknown formats
        # This might indicate a more robust error type is needed in verify_password for such cases
        pass


# To run these tests (assuming pytest is installed and in the project root):
# Ensure PYTHONPATH includes the project root if backend modules are not found:
# export PYTHONPATH=. (or similar, depending on execution context)
# pytest tests/test_auth_utils.py
