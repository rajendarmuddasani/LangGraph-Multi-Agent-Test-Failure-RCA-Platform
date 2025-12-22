"""
WebSocket endpoint for real-time RCA updates.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import structlog
import json
import asyncio

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/ws", tags=["WebSocket"])


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # session_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept WebSocket connection and register for session."""
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        
        self.active_connections[session_id].add(websocket)
        
        logger.info(
            "websocket_connected",
            session_id=session_id,
            total_connections=len(self.active_connections[session_id]),
        )
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """Unregister WebSocket connection."""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            
            # Clean up empty session
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        
        logger.info("websocket_disconnected", session_id=session_id)
    
    async def send_to_session(self, session_id: str, message: dict):
        """Send message to all connections for a session."""
        if session_id not in self.active_connections:
            return
        
        # Serialize message
        message_json = json.dumps(message)
        
        # Send to all connections (handle disconnections)
        disconnected = set()
        for connection in self.active_connections[session_id]:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.warning(
                    "websocket_send_failed",
                    session_id=session_id,
                    error=str(e),
                )
                disconnected.add(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection, session_id)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all active connections."""
        message_json = json.dumps(message)
        
        for session_id in list(self.active_connections.keys()):
            await self.send_to_session(session_id, message)


manager = ConnectionManager()


@router.websocket("/rca/{session_id}")
async def websocket_rca_updates(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time RCA updates.
    
    Client receives messages when:
    - Agent starts/completes
    - New finding discovered
    - Hypothesis updated
    - Status changes
    """
    await manager.connect(websocket, session_id)
    
    try:
        # Send initial welcome message
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "Connected to RCA session updates",
        })
        
        # Keep connection alive and listen for client messages (e.g., ping)
        while True:
            data = await websocket.receive_text()
            
            # Handle ping/pong
            if data == "ping":
                await websocket.send_json({"type": "pong"})
            
            # Handle client requests (optional)
            try:
                client_msg = json.loads(data)
                if client_msg.get("type") == "request_status":
                    # Send current status (would query DB in production)
                    await websocket.send_json({
                        "type": "status_update",
                        "session_id": session_id,
                        "status": "running",
                        "progress": 45,
                    })
            except json.JSONDecodeError:
                pass
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
        logger.info("client_disconnected", session_id=session_id)


async def notify_agent_update(session_id: str, agent_name: str, status: str, message: str):
    """
    Send agent update to all connected clients for session.
    
    Called by orchestrator during RCA workflow.
    """
    await manager.send_to_session(session_id, {
        "type": "agent_update",
        "session_id": session_id,
        "agent": agent_name,
        "status": status,
        "message": message,
        "timestamp": str(asyncio.get_event_loop().time()),
    })


async def notify_hypothesis_update(
    session_id: str,
    hypothesis: str,
    confidence: float,
    rank: int,
):
    """Send hypothesis update to connected clients."""
    await manager.send_to_session(session_id, {
        "type": "hypothesis_update",
        "session_id": session_id,
        "hypothesis": hypothesis,
        "confidence": confidence,
        "rank": rank,
        "timestamp": str(asyncio.get_event_loop().time()),
    })


async def notify_status_change(session_id: str, status: str, progress: int):
    """Send status change to connected clients."""
    await manager.send_to_session(session_id, {
        "type": "status_change",
        "session_id": session_id,
        "status": status,
        "progress": progress,
        "timestamp": str(asyncio.get_event_loop().time()),
    })
