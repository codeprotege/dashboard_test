import streamlit as st
import websockets # Using the websockets library directly for client-side
import asyncio
import os
from frontend.utils import get_backend_url # To construct WebSocket URL

st.set_page_config(page_title="WebSocket Test", layout="centered")
st.title("🧪 WebSocket Test Page")

if not st.session_state.get("auth_token"):
    st.warning("Please log in to test WebSockets (though this example is unauthenticated).")
    if st.button("Go to Login"):
        st.switch_page("pages/01_Login.py")
    st.stop()

# Construct WebSocket URL from backend URL
# Backend URL is like http://localhost:8000, WS URL will be ws://localhost:8000/ws_example/{client_id}
backend_http_url = get_backend_url()
ws_base_url = backend_http_url.replace("http", "ws")

client_id = st.text_input("Enter your Client ID for WebSocket", value=st.session_state.user_info.get("username", "test_client"), key="ws_client_id")

if "ws_messages" not in st.session_state:
    st.session_state.ws_messages = []

async def connect_and_listen(uri: str):
    try:
        async with websockets.connect(uri) as websocket:
            st.session_state.ws_messages.append(f"System: Connected to {uri}")
            st.rerun() # Update UI to show connected message

            # Send an initial message
            initial_msg = f"Hello from client {client_id}!"
            await websocket.send(initial_msg)
            st.session_state.ws_messages.append(f"You ({client_id}): {initial_msg}")
            st.rerun()

            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=300) # 5 min timeout for messages
                    st.session_state.ws_messages.append(f"Server: {message}")
                    st.rerun() # Update UI with new message
                except asyncio.TimeoutError:
                    # No message received, can send a keep-alive or just continue listening
                    # print("WebSocket receive timeout, still listening...") # Debug only
                    pass # Continue listening
                except websockets.exceptions.ConnectionClosed:
                    st.session_state.ws_messages.append("System: Connection closed by server.")
                    st.rerun()
                    break
    except Exception as e:
        st.session_state.ws_messages.append(f"System: Error connecting or during connection - {e}")
        st.rerun()

message_to_send = st.text_input("Send a message:", key="ws_message_input")

if st.button("Connect to WebSocket Example", key="ws_connect_btn") and client_id:
    uri = f"{ws_base_url}/ws_example/{client_id}"
    st.info(f"Attempting to connect to: {uri}")
    # Clear previous messages on new connection attempt
    st.session_state.ws_messages = []
    # Run the async function. Streamlit doesn't natively support top-level await or running async from buttons easily.
    # A common workaround is to run it in a separate thread or use st.experimental_singleton or similar patterns
    # for managing the connection state. For a simple test, we'll just launch it.
    # This simple launch might have issues with Streamlit's execution model for long-lived connections.
    # For robust implementation, a more advanced state management for the websocket connection is needed.

    # This is a simplified approach for a test page.
    # In a real app, you'd manage the websocket connection lifecycle more carefully.
    try:
        # This direct asyncio.run here is problematic in Streamlit's thread.
        # st.write("Note: Live WebSocket listening in Streamlit requires advanced handling. This is a basic send/receive test ability.")
        # For now, let's just try to send one message upon connect for test, and display received.
        # A full duplex chat here is tricky with basic Streamlit.

        # Let's simulate a send button instead of a persistent connection for this test page.
        # The `connect_and_listen` function is designed for persistent listening which Streamlit struggles with.
        # We will adapt this to a send/receive pattern on button click for simplicity here.
        st.session_state.ws_uri_to_connect = uri
        st.session_state.ws_connection_active = False # Flag to manage connection
        st.success(f"WebSocket URI set. Click 'Send Message' to connect and send, or 'Receive' to listen.")

    except Exception as e:
         st.error(f"Failed to initiate WebSocket connection logic: {e}")


if st.button("Send Message via WebSocket", key="ws_send_btn") and client_id and message_to_send:
    if "ws_uri_to_connect" not in st.session_state or not st.session_state.ws_uri_to_connect:
        st.error("Please 'Connect to WebSocket Example' first to set the URI.")
    else:
        uri = st.session_state.ws_uri_to_connect

        async def send_one_message(uri_to_send, msg_to_send, current_client_id):
            try:
                async with websockets.connect(uri_to_send) as websocket:
                    st.session_state.ws_messages.append(f"System: Connected to send: {msg_to_send}")
                    await websocket.send(msg_to_send)
                    st.session_state.ws_messages.append(f"You ({current_client_id}): {msg_to_send}")
                    # Attempt to receive a quick response / broadcast echo
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=2)
                        st.session_state.ws_messages.append(f"Server (quick recv): {response}")
                    except asyncio.TimeoutError:
                        st.session_state.ws_messages.append(f"System: No immediate response from server after send.")
                    except websockets.exceptions.ConnectionClosed:
                        st.session_state.ws_messages.append("System: Connection closed by server after send.")
                    st.rerun()
            except Exception as e:
                st.session_state.ws_messages.append(f"System: Error sending message - {e}")
                st.rerun()

        asyncio.run(send_one_message(uri, f"{client_id} says: {message_to_send}", client_id))
        # Clear the input box after sending
        # This needs st.text_input to have a default controlled by session_state or use st.empty() trick
        # For simplicity, user has to clear it manually for now.


st.subheader("WebSocket Messages:")
if st.session_state.ws_messages:
    # Display messages in reverse order (newest first)
    for msg in reversed(st.session_state.ws_messages):
        st.text(msg)
else:
    st.info("No WebSocket messages yet.")

st.caption("Note: This is a basic test page. Robust WebSocket integration in Streamlit for real-time persistent communication can be complex and may require external libraries or more advanced state management.")
