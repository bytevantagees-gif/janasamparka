"""
Real-time updates service using WebSockets
"""
import json
from typing import Dict, List, Set, Any, Optional
from datetime import datetime
from enum import Enum
import asyncio

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.core.cache import cache_manager
from app.models.user import User


class EventType(Enum):
    """Real-time event types"""
    COMPLAINT_CREATED = "complaint_created"
    COMPLAINT_UPDATED = "complaint_updated"
    COMPLAINT_ASSIGNED = "complaint_assigned"
    COMPLAINT_STATUS_CHANGED = "complaint_status_changed"
    COMPLAINT_RESOLVED = "complaint_resolved"
    USER_ONLINE = "user_online"
    USER_OFFLINE = "user_offline"
    DEPARTMENT_UPDATE = "department_update"
    EMERGENCY_ALERT = "emergency_alert"
    SYSTEM_NOTIFICATION = "system_notification"


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Active connections by user_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        # Room subscriptions (for constituency-based updates)
        self.room_subscriptions: Dict[str, Set[str]] = {}  # room_id -> set of user_ids
    
    async def connect(self, websocket: WebSocket, user_id: str, 
                     constituency_id: Optional[str] = None, 
                     user_role: str = "citizen"):
        """Accept and register WebSocket connection"""
        await websocket.accept()
        
        # Add to user connections
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        # Store connection metadata
        self.connection_metadata[websocket] = {
            "user_id": user_id,
            "constituency_id": constituency_id,
            "user_role": user_role,
            "connected_at": datetime.utcnow(),
            "last_ping": datetime.utcnow()
        }
        
        # Subscribe to constituency room if applicable
        if constituency_id:
            await self.subscribe_to_room(websocket, constituency_id)
        
        # Cache online status
        await cache_manager.set("online_status", [user_id], True, ttl=300)
        
        # Broadcast user online event
        await self.broadcast_user_status(user_id, True, constituency_id)
        
        logger.info("WebSocket connected", user_id=user_id, 
                   constituency_id=constituency_id, role=user_role)
    
    async def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.connection_metadata:
            metadata = self.connection_metadata[websocket]
            user_id = metadata["user_id"]
            constituency_id = metadata["constituency_id"]
            
            # Remove from user connections
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
                    
                    # Update cache for offline status
                    await cache_manager.delete("online_status", [user_id])
                    
                    # Broadcast user offline event
                    await self.broadcast_user_status(user_id, False, constituency_id)
            
            # Remove from room subscriptions
            if constituency_id:
                await self.unsubscribe_from_room(websocket, constituency_id)
            
            # Remove metadata
            del self.connection_metadata[websocket]
        
        logger.info("WebSocket disconnected", user_id=user_id)
    
    async def subscribe_to_room(self, websocket: WebSocket, room_id: str):
        """Subscribe connection to a room"""
        if websocket in self.connection_metadata:
            user_id = self.connection_metadata[websocket]["user_id"]
            
            if room_id not in self.room_subscriptions:
                self.room_subscriptions[room_id] = set()
            self.room_subscriptions[room_id].add(user_id)
            
            logger.info("User subscribed to room", user_id=user_id, room_id=room_id)
    
    async def unsubscribe_from_room(self, websocket: WebSocket, room_id: str):
        """Unsubscribe connection from a room"""
        if websocket in self.connection_metadata:
            user_id = self.connection_metadata[websocket]["user_id"]
            
            if room_id in self.room_subscriptions:
                self.room_subscriptions[room_id].discard(user_id)
                if not self.room_subscriptions[room_id]:
                    del self.room_subscriptions[room_id]
            
            logger.info("User unsubscribed from room", user_id=user_id, room_id=room_id)
    
    async def send_personal_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error("Failed to send personal message", error=str(e))
            await self.disconnect(websocket)
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send message to all connections for a user"""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error("Failed to send message to user", 
                               user_id=user_id, error=str(e))
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for connection in disconnected:
                await self.disconnect(connection)
    
    async def broadcast_to_room(self, room_id: str, message: Dict[str, Any], 
                               exclude_user: Optional[str] = None):
        """Broadcast message to all users in a room"""
        if room_id in self.room_subscriptions:
            for user_id in self.room_subscriptions[room_id]:
                if exclude_user and user_id == exclude_user:
                    continue
                await self.send_to_user(user_id, message)
    
    async def broadcast_to_role(self, role: str, message: Dict[str, Any],
                               constituency_id: Optional[str] = None):
        """Broadcast message to all users with specific role"""
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                if connection in self.connection_metadata:
                    metadata = self.connection_metadata[connection]
                    if (metadata["user_role"] == role and 
                        (constituency_id is None or metadata["constituency_id"] == constituency_id)):
                        await self.send_to_user(user_id, message)
    
    async def broadcast_user_status(self, user_id: str, online: bool, 
                                   constituency_id: Optional[str] = None):
        """Broadcast user online/offline status"""
        message = {
            "type": EventType.USER_ONLINE.value if online else EventType.USER_OFFLINE.value,
            "data": {
                "user_id": user_id,
                "online": online,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # Send to constituency room if applicable
        if constituency_id:
            await self.broadcast_to_room(constituency_id, message, exclude_user=user_id)
        
        # Send to admin users
        await self.broadcast_to_role("admin", message)
    
    async def get_online_users(self, constituency_id: Optional[str] = None) -> List[str]:
        """Get list of online users"""
        online_users = []
        
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                if connection in self.connection_metadata:
                    metadata = self.connection_metadata[connection]
                    if constituency_id is None or metadata["constituency_id"] == constituency_id:
                        online_users.append(user_id)
                        break
        
        return list(set(online_users))
    
    async def ping_connections(self):
        """Ping all active connections to check connectivity"""
        current_time = datetime.utcnow()
        disconnected = []
        
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                if connection in self.connection_metadata:
                    metadata = self.connection_metadata[connection]
                    last_ping = metadata["last_ping"]
                    
                    # Check if connection is stale (5 minutes)
                    if (current_time - last_ping).total_seconds() > 300:
                        disconnected.append(connection)
                        continue
                    
                    # Send ping
                    try:
                        await connection.send_text(json.dumps({"type": "ping"}))
                        metadata["last_ping"] = current_time
                    except Exception:
                        disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            await self.disconnect(connection)
        
        logger.info("Connection ping completed", 
                   active_connections=len(self.active_connections),
                   disconnected=len(disconnected))


class RealtimeEventService:
    """Service for handling real-time events"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
    
    async def notify_complaint_created(self, complaint_data: Dict[str, Any]):
        """Notify about new complaint creation"""
        message = {
            "type": EventType.COMPLAINT_CREATED.value,
            "data": {
                "complaint": complaint_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        constituency_id = complaint_data.get("constituency_id")
        
        # Notify constituency users
        if constituency_id:
            await self.connection_manager.broadcast_to_room(
                constituency_id, message
            )
        
        # Notify department users if assigned
        dept_id = complaint_data.get("dept_id")
        if dept_id:
            await self.connection_manager.broadcast_to_role(
                "department_officer", message, constituency_id
            )
        
        # Notify admins
        await self.connection_manager.broadcast_to_role("admin", message)
    
    async def notify_complaint_updated(self, complaint_data: Dict[str, Any], 
                                      changed_by: str):
        """Notify about complaint update"""
        message = {
            "type": EventType.COMPLAINT_UPDATED.value,
            "data": {
                "complaint": complaint_data,
                "changed_by": changed_by,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        constituency_id = complaint_data.get("constituency_id")
        
        # Notify complaint creator
        user_id = complaint_data.get("user_id")
        if user_id:
            await self.connection_manager.send_to_user(user_id, message)
        
        # Notify constituency users
        if constituency_id:
            await self.connection_manager.broadcast_to_room(
                constituency_id, message, exclude_user=user_id
            )
        
        # Notify admins
        await self.connection_manager.broadcast_to_role("admin", message)
    
    async def notify_complaint_assigned(self, complaint_data: Dict[str, Any], 
                                       department_id: str):
        """Notify about complaint assignment"""
        message = {
            "type": EventType.COMPLAINT_ASSIGNED.value,
            "data": {
                "complaint": complaint_data,
                "department_id": department_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        constituency_id = complaint_data.get("constituency_id")
        
        # Notify department officers
        await self.connection_manager.broadcast_to_role(
            "department_officer", message, constituency_id
        )
        
        # Notify MLA/Moderator
        await self.connection_manager.broadcast_to_role(
            "mla", message, constituency_id
        )
        await self.connection_manager.broadcast_to_role(
            "moderator", message, constituency_id
        )
    
    async def notify_status_changed(self, complaint_data: Dict[str, Any], 
                                   old_status: str, new_status: str,
                                   changed_by: str):
        """Notify about complaint status change"""
        message = {
            "type": EventType.COMPLAINT_STATUS_CHANGED.value,
            "data": {
                "complaint": complaint_data,
                "old_status": old_status,
                "new_status": new_status,
                "changed_by": changed_by,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        constituency_id = complaint_data.get("constituency_id")
        user_id = complaint_data.get("user_id")
        
        # Notify complaint creator
        if user_id:
            await self.connection_manager.send_to_user(user_id, message)
        
        # Notify constituency users
        if constituency_id:
            await self.connection_manager.broadcast_to_room(
                constituency_id, message, exclude_user=user_id
            )
        
        # Notify admins
        await self.connection_manager.broadcast_to_role("admin", message)
    
    async def notify_emergency_alert(self, complaint_data: Dict[str, Any]):
        """Notify about emergency complaint"""
        message = {
            "type": EventType.EMERGENCY_ALERT.value,
            "data": {
                "complaint": complaint_data,
                "priority": "urgent",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        constituency_id = complaint_data.get("constituency_id")
        
        # Emergency notifications to all roles
        await self.connection_manager.broadcast_to_role("admin", message)
        await self.connection_manager.broadcast_to_role("mla", message, constituency_id)
        await self.connection_manager.broadcast_to_role("moderator", message, constituency_id)
        await self.connection_manager.broadcast_to_role("department_officer", message, constituency_id)
        
        # Also notify nearby users (within 1km)
        if complaint_data.get("lat") and complaint_data.get("lng"):
            # This would integrate with location service to find nearby users
            pass
    
    async def notify_system_notification(self, notification: Dict[str, Any],
                                        target_role: Optional[str] = None,
                                        constituency_id: Optional[str] = None):
        """Send system notification"""
        message = {
            "type": EventType.SYSTEM_NOTIFICATION.value,
            "data": {
                "notification": notification,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        if target_role:
            await self.connection_manager.broadcast_to_role(
                target_role, message, constituency_id
            )
        elif constituency_id:
            await self.connection_manager.broadcast_to_room(
                constituency_id, message
            )
        else:
            # Broadcast to all
            for user_id in self.connection_manager.active_connections:
                await self.connection_manager.send_to_user(user_id, message)


# Global instances
connection_manager = ConnectionManager()
realtime_service = RealtimeEventService(connection_manager)


async def websocket_endpoint(websocket: WebSocket, user_id: str, 
                           constituency_id: Optional[str] = None,
                           user_role: str = "citizen"):
    """WebSocket endpoint for real-time updates"""
    try:
        await connection_manager.connect(websocket, user_id, constituency_id, user_role)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await connection_manager.send_personal_message(websocket, {"type": "pong"})
            elif message.get("type") == "subscribe_room":
                room_id = message.get("room_id")
                if room_id:
                    await connection_manager.subscribe_to_room(websocket, room_id)
            elif message.get("type") == "unsubscribe_room":
                room_id = message.get("room_id")
                if room_id:
                    await connection_manager.unsubscribe_from_room(websocket, room_id)
            
    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket error", user_id=user_id, error=str(e))
        await connection_manager.disconnect(websocket)


# Background task for connection health monitoring
async def monitor_connections():
    """Background task to monitor connection health"""
    while True:
        await connection_manager.ping_connections()
        await asyncio.sleep(60)  # Check every minute
