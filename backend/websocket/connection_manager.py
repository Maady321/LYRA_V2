from fastapi import WebSocket
from typing import Dict, Set
from backend.core.logger import logger

class ConnectionManager:
    def __init__(self):
        # Store active connections
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        """Register a new active WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        """Unregister a disconnected WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Remaining connections: {len(self.active_connections)}")

    async def send_json(self, websocket: WebSocket, data: dict) -> None:
        """Send JSON payload directly to a specific socket connection"""
        if websocket in self.active_connections:
            try:
                await websocket.send_json(data)
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
                self.disconnect(websocket)

    async def broadcast_json(self, data: dict) -> None:
        """Broadcast JSON payload to all active socket connections"""
        logger.info(f"Broadcasting message to {len(self.active_connections)} sockets")
        disconnected_sockets = set()
        for websocket in self.active_connections:
            try:
                await websocket.send_json(data)
            except Exception as e:
                logger.error(f"Error broadcasting WebSocket message: {e}")
                disconnected_sockets.add(websocket)
                
        for ws in disconnected_sockets:
            self.disconnect(ws)

manager = ConnectionManager()
