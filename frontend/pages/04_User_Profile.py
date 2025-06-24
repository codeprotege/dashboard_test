import streamlit as st
from frontend.utils import api_call

st.set_page_config(page_title="User Profile", layout="centered")
st.title("⚙️ User Profile")

if not st.session_state.get("auth_token"):
    st.warning("Please log in to view your profile.")
    if st.button("Go to Login"):
        st.switch_page("pages/01_Login.py")
    st.stop()

st.subheader("Your Account Details")

user_info = st.session_state.get("user_info")

if user_info:
    st.write(f"**Username:** {user_info.get('username')}")
    st.write(f"**Email:** {user_info.get('email')}")
    st.write(f"**User ID:** {user_info.get('id')}")
    st.write(f"**Active Account:** {'Yes' if user_info.get('is_active') else 'No'}")
    st.write(f"**Administrator:** {'Yes' if user_info.get('is_superuser') else 'No'}")

    created_at_str = user_info.get('created_at', '')
    # Attempt to parse and format datetime if it's a string
    try:
        from dateutil import parser
        created_at_dt = parser.isoparse(created_at_str)
        st.write(f"**Joined:** {created_at_dt.strftime('%Y-%m-%d %H:%M:%S %Z') if created_at_dt else 'N/A'}")
    except (ValueError, TypeError):
        st.write(f"**Joined:** {created_at_str if created_at_str else 'N/A'}")


    st.divider()
    st.subheader("Update Profile Information")

    with st.form("update_profile_form"):
        # Username update might be restricted or have specific rules
        new_username = st.text_input("New Username (optional, min 3 chars)", value=user_info.get('username'))
        new_email = st.text_input("New Email (optional)", value=user_info.get('email'))
        # For sensitive changes like password, usually a separate form/flow is better
        # For is_active/is_superuser, typically only admins should change these via a separate interface

        update_submit = st.form_submit_button("Save Changes")

        if update_submit:
            payload = {}
            if new_username and new_username != user_info.get('username'):
                if len(new_username) < 3:
                    st.error("Username must be at least 3 characters.")
                else:
                    payload["username"] = new_username

            if new_email and new_email != user_info.get('email'):
                # Basic email format check (Pydantic on backend does more)
                if "@" not in new_email or "." not in new_email.split("@")[-1]:
                     st.error("Please enter a valid email address.")
                else:
                    payload["email"] = new_email

            if payload: # If there are actual changes
                user_id = user_info.get("id")
                response = api_call(
                    method="PUT",
                    endpoint=f"/users/{user_id}",
                    token=st.session_state.auth_token,
                    json_data=payload
                )
                if response: # api_call returns None on error, response dict on success
                    st.success("Profile updated successfully!")
                    # Re-fetch user info to update session state and display
                    updated_user_info = api_call("GET", "/users/me", token=st.session_state.auth_token)
                    if updated_user_info:
                        st.session_state.user_info = updated_user_info
                        st.rerun() # Rerun to reflect changes immediately
                    else:
                        st.warning("Profile updated, but could not refresh display. Please reload.")
                # If response is None, api_call already showed an error.
            else:
                st.info("No changes detected to update.")
else:
    st.error("Could not load user information. Please try logging out and back in.")

# Option to change password (would typically navigate to a new form/page)
    st.divider()
    st.subheader("Change Password")
    with st.form("change_password_form"):
        old_password = st.text_input("Current Password", type="password", key="old_pass")
        new_password = st.text_input("New Password (min 8 characters)", type="password", key="new_pass")
        confirm_new_password = st.text_input("Confirm New Password", type="password", key="confirm_new_pass")
        change_password_submit = st.form_submit_button("Change Password")

        if change_password_submit:
            if not all([old_password, new_password, confirm_new_password]):
                st.error("Please fill in all password fields.")
            elif new_password != confirm_new_password:
                st.error("New passwords do not match.")
            elif len(new_password) < 8:
                st.error("New password must be at least 8 characters long.")
            elif old_password == new_password:
                st.error("New password cannot be the same as the old password.")
            else:
                password_payload = {
                    "old_password": old_password,
                    "new_password": new_password
                }
                response = api_call(
                    method="POST",
                    endpoint="/users/me/change-password",
                    token=st.session_state.auth_token,
                    json_data=password_payload
                )
                if response and response.get("message") == "Password updated successfully":
                    st.success("Password changed successfully!")
                    st.info("You may need to log in again with your new password if your session is invalidated by this change elsewhere, though typically token remains valid until expiry.")
                # If response is None or message is different, api_call would have shown an error from backend
                # e.g. "Incorrect old password" or other validation issues.
                # No specific error handling here needed unless we want to customize frontend message further.

# General navigation button, could be useful at the bottom
# if st.button("Back to Home Dashboard", key="profile_back_home_dashboard"):
#     st.switch_page("app.py")
