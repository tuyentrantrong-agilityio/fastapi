"""
WebSocket Chat & Notification System Example

WebSocket: Real-time bidirectional communication
- Server → Client: Push notifications, chat messages
- Client → Server: Send messages, subscribe to events

Usage:
  python websocket_chat_example.py

  Then open browser:
  http://localhost:8000 (HTML client)
  or use wscat:
  wscat -c ws://localhost:8000/ws/user123
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from datetime import datetime
import json
import uuid
import os

# ============================================================================
# CONNECTION MANAGER - Manage multiple WebSocket connections
# ============================================================================


class ConnectionManager:
    """Manage active WebSocket connections for chat/notifications"""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        """Accept new connection, add to user's connection list"""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(websocket)
        print(
            f"[WS] User {user_id} connected (Total: {len(self.active_connections[user_id])})"
        )

    async def disconnect(self, user_id: str, websocket: WebSocket):
        """Remove connection when user disconnects"""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        print(f"[WS] User {user_id} disconnected")

    async def send_personal(self, user_id: str, message: dict):
        """Send message to specific user's all connections"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

    async def broadcast(self, message: dict, exclude_user: str = None):
        """Send message to all connected users"""
        for user_id, connections in self.active_connections.items():
            if exclude_user and user_id == exclude_user:
                continue

            for connection in connections:
                try:
                    await connection.send_json(message)
                except:
                    pass

    async def broadcast_to_room(
        self, room_id: str, message: dict, exclude_user: str = None
    ):
        """Send message to all users in a room"""
        for user_id, connections in self.active_connections.items():
            if exclude_user and user_id == exclude_user:
                continue

            for connection in connections:
                try:
                    await connection.send_json(message)
                except:
                    pass

    def get_users_online(self) -> list[str]:
        """Get list of online users"""
        return list(self.active_connections.keys())

    def get_active_count(self) -> int:
        """Get total active connections"""
        total = 0
        for connections in self.active_connections.values():
            total += len(connections)
        return total


# ============================================================================
# INITIALIZATION
# ============================================================================

manager = ConnectionManager()
chat_history = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Server startup/shutdown"""
    print("\n" + "=" * 60)
    print("WebSocket Chat Server Starting")
    print("=" * 60)
    print("Endpoints:")
    print("  GET  /              - Chat interface")
    print("  WS   /ws/{user_id}  - WebSocket connection")
    print("=" * 60 + "\n")

    yield

    print("\n" + "=" * 60)
    print("Server shutting down")
    print("=" * 60 + "\n")


app = FastAPI(title="WebSocket Chat & Notification", lifespan=lifespan)


# ============================================================================
# ROUTES
# ============================================================================


@app.get("/")
async def get_chat():
    """Serve chat HTML client from templates folder"""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "chat.html")
    return FileResponse(template_path, media_type="text/html")


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for chat

    Flow:
    1. Client connects: ws://localhost:8000/ws/user123
    2. Server accepts connection
    3. Client sends/receives messages
    4. On disconnect: clean up
    """
    await manager.connect(user_id, websocket)

    try:
        # Broadcast user joined
        await manager.broadcast(
            {
                "type": "system",
                "message": f"✓ {user_id} joined the chat",
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Send online users list
        await websocket.send_json(
            {
                "type": "system",
                "message": f"Online users: {', '.join(manager.get_users_online())}",
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Listen for messages from client
        while True:
            data = await websocket.receive_json()

            if data["type"] == "message":
                message_obj = {
                    "type": "chat",
                    "user": user_id,
                    "message": data["text"],
                    "timestamp": data.get("timestamp", datetime.now().isoformat()),
                }

                chat_history.append(message_obj)

                # Broadcast to all users
                await manager.broadcast(message_obj)

                print(f"[CHAT] {user_id}: {data['text']}")

    except WebSocketDisconnect:
        await manager.disconnect(user_id, websocket)

        # Broadcast user left
        await manager.broadcast(
            {
                "type": "system",
                "message": f"✗ {user_id} left the chat",
                "timestamp": datetime.now().isoformat(),
            }
        )


# ============================================================================
# NOTIFICATION ENDPOINTS (REST + WebSocket)
# ============================================================================


@app.post("/notify/{user_id}")
async def send_notification(user_id: str, title: str, message: str):
    """Send notification to specific user via WebSocket"""
    if user_id not in manager.active_connections:
        raise HTTPException(status_code=404, detail="User not connected")

    await manager.send_personal(
        user_id,
        {
            "type": "notification",
            "title": title,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        },
    )

    print(f"[NOTIFY] {title} → {user_id}")

    return {"status": "sent", "user": user_id}


@app.post("/notify/all")
async def broadcast_notification(title: str, message: str):
    """Send notification to all connected users"""
    await manager.broadcast(
        {
            "type": "notification",
            "title": title,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }
    )

    print(f"[NOTIFY-ALL] {title}")

    return {"status": "sent", "users": manager.get_users_online()}


@app.get("/status")
async def get_status():
    """Get server status and connected users"""
    return {
        "status": "running",
        "users_online": manager.get_users_online(),
        "total_connections": manager.get_active_count(),
        "chat_messages": len(chat_history),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/chat/history")
async def get_chat_history(limit: int = 50):
    """Get chat history"""
    return {"messages": chat_history[-limit:], "total": len(chat_history)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
