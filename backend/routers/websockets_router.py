from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status as ws_status
from typing import List, Annotated, Dict, Optional # Added Optional
import asyncio # For concurrent tasks if needed

# from backend.auth import get_current_user # For authenticated WebSockets (more complex setup)
# from backend.models import User
# from backend.database import get_db
# from sqlalchemy.orm import Session

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Store connections with an identifier, e.g., client_id or username
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"Client {client_id} connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"Client {client_id} disconnected. Total clients: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

    async def broadcast(self, message: str, exclude_client_id: Optional[str] = None):
        # Create a list of tasks for sending messages concurrently
        tasks = []
        for client_id, connection in self.active_connections.items():
            if client_id == exclude_client_id:
                continue
            tasks.append(connection.send_text(message))
        await asyncio.gather(*tasks) # Execute all send tasks

manager = ConnectionManager()

@router.websocket("/ws/{client_id}", name="WebSocket Example Endpoint") # Simple unauthenticated WebSocket endpoint
async def websocket_endpoint_unauth(websocket: WebSocket, client_id: str):
    """
    Unauthenticated WebSocket example endpoint.
    `client_id` is a path parameter identifying the client.
    """
    # Prevent duplicate client_id connections if desired, or handle gracefully
    if client_id in manager.active_connections:
        print(f"Client ID {client_id} already connected. Closing new connection.")
        await websocket.accept() # Must accept before close with code
        await websocket.close(code=ws_status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, client_id)
    await manager.broadcast(f"System: Client '{client_id}' joined the session.")

    try:
        while True:
            data = await websocket.receive_text()
            # Echo back to sender
            await manager.send_personal_message(f"You ({client_id}) sent: {data}", client_id)
            # Broadcast to others
            await manager.broadcast(f"Client '{client_id}' says: {data}", exclude_client_id=client_id)
    except WebSocketDisconnect:
        print(f"WebSocketDisconnect for client: {client_id}")
    except Exception as e:
        print(f"Error in WebSocket for client {client_id}: {e}")
    finally: # Ensure disconnect is handled
        manager.disconnect(client_id)
        await manager.broadcast(f"System: Client '{client_id}' left the session.")

# TODO: Implement authenticated WebSocket endpoint if needed.
# This requires a mechanism to pass the JWT token (e.g., query param, subprotocol)
# and validate it using a modified `get_current_user` or similar.
# Example:
# @router.websocket("/ws_auth")
# async def websocket_endpoint_auth(
#     websocket: WebSocket,
#     token: Annotated[str | None, Query()] = None, # Token via query: ws://.../?token=xxx
#     db: Annotated[Session, Depends(get_db)] = Depends() # Get DB session
# ):
#     if token is None:
#         await websocket.accept()
#         await websocket.close(code=ws_status.WS_1008_POLICY_VIOLATION, reason="Missing token")
#         return
#     try:
#         # This is a simplified version; get_current_user is async and expects HTTP context
#         # You would need a synchronous version or adapt it carefully for WS.
#         # For WS, it might be better to decode and verify token directly here.
#         from backend.auth import SECRET_KEY, ALGORITHM # Avoid circular imports
#         from jose import jwt, JWTError
#         from backend.schemas import TokenPayload
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: Optional[str] = payload.get("sub")
#         if username is None:
#             raise JWTError("User subject missing")
#         user = crud.get_user_by_username(db, username=username)
#         if not user or not user.is_active:
#             raise JWTError("User not found or inactive")
#     except JWTError as e:
#         await websocket.accept()
#         await websocket.close(code=ws_status.WS_1008_POLICY_VIOLATION, reason=f"Authentication failed: {e}")
#         return
#
#     client_id = user.username # Use username as client_id for authenticated users
#     await manager.connect(websocket, client_id)
#     await manager.broadcast(f"User '{client_id}' connected.")
#     try:
#         while True:
#             data = await websocket.receive_text()
#             await manager.broadcast(f"User '{client_id}' says: {data}", exclude_client_id=client_id)
#     except WebSocketDisconnect:
#         pass # manager.disconnect and broadcast handled in finally
#     finally:
#         manager.disconnect(client_id)
#         await manager.broadcast(f"User '{client_id}' disconnected.")
