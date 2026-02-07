"""
WebSocket Real-time Service
Live updates for tank levels, notifications, and alerts
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """WebSocket message types."""
    TANK_UPDATE = "tank_update"
    SENSOR_READING = "sensor_reading"
    NOTIFICATION = "notification"
    ALERT = "alert"
    VERIFICATION_STATUS = "verification_status"
    PAYMENT_STATUS = "payment_status"
    SYSTEM_STATUS = "system_status"
    PING = "ping"
    PONG = "pong"


@dataclass
class WSMessage:
    """WebSocket message structure."""
    type: MessageType
    data: Dict[str, Any]
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_json(self) -> str:
        return json.dumps({
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp
        })


class ConnectionManager:
    """
    Manage WebSocket connections.
    
    Features:
    - Room-based subscriptions
    - User-specific channels
    - Project-specific updates
    - Broadcast capabilities
    """
    
    def __init__(self):
        # Active connections by user
        self.user_connections: Dict[str, Set[WebSocket]] = {}
        
        # Project subscriptions (project_id -> set of user_ids)
        self.project_subscriptions: Dict[int, Set[str]] = {}
        
        # All active connections
        self.active_connections: Set[WebSocket] = set()
        
        # Connection metadata
        self.connection_info: Dict[WebSocket, Dict] = {}
    
    async def connect(
        self,
        websocket: WebSocket,
        user_id: str,
        subscriptions: List[int] = None
    ):
        """Accept new WebSocket connection."""
        await websocket.accept()
        
        # Track connection
        self.active_connections.add(websocket)
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)
        
        # Store metadata
        self.connection_info[websocket] = {
            "user_id": user_id,
            "connected_at": datetime.utcnow(),
            "subscriptions": subscriptions or []
        }
        
        # Subscribe to projects
        if subscriptions:
            for project_id in subscriptions:
                if project_id not in self.project_subscriptions:
                    self.project_subscriptions[project_id] = set()
                self.project_subscriptions[project_id].add(user_id)
        
        logger.info(f"WebSocket connected: user={user_id}, projects={subscriptions}")
        
        # Send welcome message
        await self.send_personal(user_id, WSMessage(
            type=MessageType.SYSTEM_STATUS,
            data={"status": "connected", "message": "Welcome to RainForge Live"}
        ))
    
    def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection."""
        self.active_connections.discard(websocket)
        
        info = self.connection_info.get(websocket, {})
        user_id = info.get("user_id")
        
        if user_id:
            if user_id in self.user_connections:
                self.user_connections[user_id].discard(websocket)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            # Remove from project subscriptions
            for project_id, users in self.project_subscriptions.items():
                users.discard(user_id)
        
        if websocket in self.connection_info:
            del self.connection_info[websocket]
        
        logger.info(f"WebSocket disconnected: user={user_id}")
    
    async def send_personal(self, user_id: str, message: WSMessage):
        """Send message to specific user."""
        if user_id in self.user_connections:
            disconnected = set()
            for websocket in self.user_connections[user_id]:
                try:
                    await websocket.send_text(message.to_json())
                except:
                    disconnected.add(websocket)
            
            # Clean up disconnected
            for ws in disconnected:
                self.disconnect(ws)
    
    async def send_to_project(self, project_id: int, message: WSMessage):
        """Send message to all users subscribed to a project."""
        if project_id in self.project_subscriptions:
            for user_id in self.project_subscriptions[project_id]:
                await self.send_personal(user_id, message)
    
    async def broadcast(self, message: WSMessage):
        """Broadcast message to all connected clients."""
        disconnected = set()
        
        for websocket in self.active_connections:
            try:
                await websocket.send_text(message.to_json())
            except:
                disconnected.add(websocket)
        
        for ws in disconnected:
            self.disconnect(ws)
    
    async def broadcast_tank_update(
        self,
        project_id: int,
        tank_level: float,
        capacity: float,
        sensor_id: str
    ):
        """Broadcast tank level update."""
        message = WSMessage(
            type=MessageType.TANK_UPDATE,
            data={
                "project_id": project_id,
                "tank_level_percent": tank_level,
                "capacity_liters": capacity,
                "current_liters": capacity * (tank_level / 100),
                "sensor_id": sensor_id
            }
        )
        await self.send_to_project(project_id, message)
    
    async def send_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str = "info",
        data: Dict = None
    ):
        """Send notification to user."""
        ws_message = WSMessage(
            type=MessageType.NOTIFICATION,
            data={
                "title": title,
                "message": message,
                "notification_type": notification_type,
                "extra": data or {}
            }
        )
        await self.send_personal(user_id, ws_message)
    
    async def send_alert(
        self,
        user_id: str,
        alert_type: str,
        severity: str,
        message: str,
        project_id: int = None
    ):
        """Send alert to user."""
        ws_message = WSMessage(
            type=MessageType.ALERT,
            data={
                "alert_type": alert_type,
                "severity": severity,
                "message": message,
                "project_id": project_id
            }
        )
        await self.send_personal(user_id, ws_message)
    
    def get_connection_stats(self) -> Dict:
        """Get connection statistics."""
        return {
            "total_connections": len(self.active_connections),
            "unique_users": len(self.user_connections),
            "project_subscriptions": {
                k: len(v) for k, v in self.project_subscriptions.items()
            }
        }


# Global connection manager
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint handler."""
    # Get subscription list from query params
    subscriptions = websocket.query_params.get("projects", "")
    project_ids = [int(p) for p in subscriptions.split(",") if p.isdigit()]
    
    await manager.connect(websocket, user_id, project_ids)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                # Handle ping
                if message.get("type") == "ping":
                    await websocket.send_text(WSMessage(
                        type=MessageType.PONG,
                        data={"received": message.get("timestamp")}
                    ).to_json())
                
                # Handle subscription updates
                elif message.get("type") == "subscribe":
                    project_id = message.get("project_id")
                    if project_id:
                        if project_id not in manager.project_subscriptions:
                            manager.project_subscriptions[project_id] = set()
                        manager.project_subscriptions[project_id].add(user_id)
                
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager."""
    return manager
