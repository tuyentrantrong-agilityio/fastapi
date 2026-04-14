"""WebSocket Connection Manager - handles real-time task updates"""

from typing import Set, Dict, List
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and subscriptions for real-time task updates"""
    
    def __init__(self):
        # connections[user_id] = [ws1, ws2, ...]
        # Track all active WebSocket connections per user
        self.connections: Dict[int, List[WebSocket]] = {}
        
        # subscriptions[user_id][ws] = {task_1, task_2, ...}
        # Track which tasks each connection is subscribed to
        self.subscriptions: Dict[int, Dict[WebSocket, Set[int]]] = {}
    
    def connect(self, user_id: int, websocket: WebSocket):
        """Add new connection from user"""
        if user_id not in self.connections:
            self.connections[user_id] = []
            self.subscriptions[user_id] = {}
        
        self.connections[user_id].append(websocket)
        self.subscriptions[user_id][websocket] = set()
        
        logger.info(f"User {user_id} connected. Total connections: {len(self.connections[user_id])}")
    
    def disconnect(self, user_id: int, websocket: WebSocket):
        """Remove connection - with safe cleanup"""
        # [OK] Safe check: don't crash if connection already removed
        if user_id in self.connections:
            if websocket in self.connections[user_id]:
                self.connections[user_id].remove(websocket)
                logger.info(f"User {user_id} disconnected. Remaining: {len(self.connections[user_id])}")
            
            # Clean up user if no connections left
            if len(self.connections[user_id]) == 0:
                del self.connections[user_id]
        
        # Remove from subscriptions (safe)
        if user_id in self.subscriptions:
            self.subscriptions[user_id].pop(websocket, None)
            
            # [OK] FIX 2.2: Clean up entire user entry if no more connections
            # (prevent memory leak of empty subscription dicts)
            if len(self.connections.get(user_id, [])) == 0:
                self.subscriptions.pop(user_id, None)
                logger.info(f"Cleaned up subscriptions for user {user_id}")
    
    async def subscribe(self, user_id: int, websocket: WebSocket, task_id: int):
        """Subscribe to task updates
        
        [WARN] NOTE: Ownership check should be done BEFORE calling this (in websocket.py)
        This method only manages state (subscriptions dict)
        [OK] FIX 2.1: Removed DB query - keep manager pure
        """
        # Simply add task_id to subscriptions
        self.subscriptions[user_id][websocket].add(task_id)
        logger.info(f"User {user_id} subscribed to task {task_id}")
    
    async def unsubscribe(self, user_id: int, websocket: WebSocket, task_id: int):
        """Unsubscribe from task updates"""
        self.subscriptions[user_id][websocket].discard(task_id)
        logger.info(f"User {user_id} unsubscribed from task {task_id}")
    
    async def broadcast_to_subscribers(self, task_id: int, message: dict):
        """Broadcast to all clients subscribed to this task"""
        dead_connections = []  # Track failed connections
        
        # Loop through all users
        for user_id, ws_dict in self.subscriptions.items():
            # Loop through all connections of this user
            for ws, subscribed_tasks in ws_dict.items():
                # Check if this connection subscribed to task_id
                if task_id in subscribed_tasks:
                    try:
                        await ws.send_json(message)
                        logger.debug(f"Sent update for task {task_id} to user {user_id}")
                    except Exception as e:
                        # [OK] Better error handling: track dead connections
                        logger.warning(f"Failed to send to user {user_id}: {e}")
                        dead_connections.append((user_id, ws))
        
        # [OK] Cleanup dead connections
        for user_id, ws in dead_connections:
            self.disconnect(user_id, ws)
            logger.info(f"Cleaned up dead connection for user {user_id}")


# [OK] CREATE GLOBAL INSTANCE HERE (not in main.py!)
manager = ConnectionManager()
