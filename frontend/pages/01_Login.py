import streamlit as st
from frontend.utils import api_call, get_backend_url # api_call for user creation, direct requests for token
import requests # For direct call to /token endpoint

st.set_page_config(page_title="Login/Register", layout="centered")

st.title("User Login / Registration")

# --- Session State Check ---
if st.session_state.get("auth_token"):
    st.info(f"You are already logged in as {st.session_state.user_info.get('username','N/A')}.")
    if st.button("Go to Dashboard"):
        st.switch_page("app.py") # Streamlit's way to switch pages
    st.stop()


tab_login, tab_register = st.tabs(["Login", "Register"])

with tab_login:
    st.subheader("Login to your Account")
    with st.form("login_form"):
        login_username = st.text_input("Username", key="login_user_field") # Unique keys
        login_password = st.text_input("Password", type="password", key="login_pass_field")
        login_submitted = st.form_submit_button("Login")

        if login_submitted:
            if not login_username or not login_password:
                st.error("Username and password are required.")
            else:
                # For OAuth2PasswordRequestForm, data must be form-encoded
                token_url = f"{get_backend_url()}/auth/token"
                try:
                    response = requests.post(
                        token_url,
                        data={"username": login_username, "password": login_password},
                        timeout=10
                    )
                    response.raise_for_status() # Check for HTTP errors
                    token_data = response.json()

                    st.session_state.auth_token = token_data.get("access_token")

                    # Fetch user details with the new token using api_call utility
                    user_info = api_call(method="GET", endpoint="/users/me", token=st.session_state.auth_token)
                    if user_info:
                        st.session_state.user_info = user_info
                        st.success(f"Login successful! Welcome {user_info.get('username')}.")
                        st.balloons()
                        # Automatically switch to dashboard after a short delay or button click
                        # For now, let user click a button to navigate
                        if st.button("Proceed to Dashboard", key="login_success_proceed"):
                             st.switch_page("app.py")
                    else:
                        # This case should ideally not happen if token is valid and /users/me works
                        st.error("Login succeeded (token received) but failed to fetch user details. Please try again.")
                        st.session_state.auth_token = None # Clear token if user details fail

                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 401: # Unauthorized
                        st.error("Login failed: Incorrect username or password.")
                    elif e.response.status_code == 400: # Bad Request (e.g. inactive user)
                        try:
                            detail = e.response.json().get("detail", "Login failed.")
                        except ValueError: # Not JSON
                            detail = e.response.text
                        st.error(f"Login failed: {detail}")
                    else: # Other HTTP errors
                        st.error(f"Login failed due to server error: Status {e.response.status_code}.")
                except requests.exceptions.RequestException: # Connection errors, timeouts
                    st.error(f"Login request error: Could not connect to the server or request timed out.")


with tab_register:
    st.subheader("Create a New Account")
    with st.form("register_form"):
        reg_username = st.text_input("Username", key="reg_user_field", help="Min 3 characters")
        reg_email = st.text_input("Email", key="reg_email_field")
        reg_password = st.text_input("Password", type="password", key="reg_pass_field", help="Min 8 characters")
        reg_confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_pass_field")
        register_submitted = st.form_submit_button("Register")

        if register_submitted:
            # Basic client-side validation
            if not all([reg_username, reg_email, reg_password, reg_confirm_password]):
                st.error("Please fill in all fields.")
            elif reg_password != reg_confirm_password:
                st.error("Passwords do not match.")
            elif len(reg_password) < 8: # Matches schema validation
                st.error("Password must be at least 8 characters long.")
            elif len(reg_username) < 3: # Matches schema validation
                st.error("Username must be at least 3 characters long.")
            else:
                user_data = {
                    "username": reg_username,
                    "email": reg_email,
                    "password": reg_password
                }
                # api_call will handle displaying errors from backend if any
                response_data = api_call(method="POST", endpoint="/users/", json_data=user_data)
                if response_data:
                    # Check if response_data contains expected user fields (like id or username from UserPublic schema)
                    if "id" in response_data and "username" in response_data:
                        st.success(f"Registration successful for {response_data.get('username')}! You can now log in using the Login tab.")
                        st.balloons()
                    else:
                        # This case means api_call returned something, but not the expected UserPublic structure.
                        # api_call itself would show an error if the status code was an HTTP error.
                        # So this might be an unexpected success response format.
                        st.warning(f"Registration attempt returned an unexpected response. Please check details or try again.")
                # If response_data is None, api_call already displayed an error.

if st.button("Back to Home", key="login_back_home"):
    st.switch_page("app.py")
