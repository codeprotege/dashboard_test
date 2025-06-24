import streamlit as st
import requests
import os

# Centralized backend URL getter
def get_backend_url():
    return os.getenv("BACKEND_URL", "http://localhost:8000")

# Example utility for making API calls
def api_call(method: str, endpoint: str, token: str = None, json_data=None, params=None, data=None):
    """
    Makes an API call to the backend.
    `method` should be "GET", "POST", "PUT", "DELETE".
    `endpoint` should start with a "/" (e.g., "/users/me").
    `token` is the JWT auth token.
    `json_data` is for POST/PUT request body (sends as JSON).
    `params` is for URL query parameters.
    `data` is for form-encoded data (e.g. for OAuth2PasswordRequestForm).
    """
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        full_url = f"{get_backend_url()}{endpoint}"
        # Note: requests.request will use 'json' if 'data' is None, and 'data' if 'json' is None.
        # If both are provided, 'data' typically takes precedence for the body.
        # For clarity, ensure only one of 'json' or 'data' is used for the body based on Content-Type.
        if json_data is not None and data is not None:
            raise ValueError("Provide either json_data or data, not both.")

        response = requests.request(method, full_url, headers=headers, json=json_data, params=params, data=data, timeout=10)
        response.raise_for_status() # Raises HTTPError for bad responses (4XX or 5XX)

        # Handle cases where response might be empty but successful (e.g., 204 No Content)
        if response.status_code == 204:
            return None
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        # Try to parse error message from response if possible
        error_detail = http_err.response.text
        try:
            error_json = http_err.response.json()
            if "detail" in error_json: # FastAPI often returns {"detail": "error message"}
                error_detail = error_json["detail"]
        except ValueError: # Response was not JSON
            pass
        st.error(f"API Error: {http_err.response.status_code} - {error_detail}")

    except requests.exceptions.ConnectionError:
        st.error(f"Connection error: Could not connect to the backend at {get_backend_url()}. Please ensure the backend is running.")
    except requests.exceptions.Timeout:
        st.error("Request timed out. The backend might be slow or unavailable.")
    except requests.exceptions.RequestException as req_err: # Catch-all for other request issues
        st.error(f"API request error: {req_err}")
    return None # Or raise an exception / return a specific error object

# Add other frontend utilities here, e.g., for formatting data, common UI elements, etc.
