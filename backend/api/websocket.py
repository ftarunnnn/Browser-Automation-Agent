import json
from typing import Dict, List, Any
from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, task_id: str, websocket: WebSocket):
        await websocket.accept()
        if task_id not in self.active_connections:
            self.active_connections[task_id] = []
        self.active_connections[task_id].append(websocket)

    def disconnect(self, task_id: str, websocket: WebSocket):
        if task_id in self.active_connections:
            if websocket in self.active_connections[task_id]:
                self.active_connections[task_id].remove(websocket)
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]

    async def broadcast_event(self, task_id: str, event_type: str, payload: Dict[str, Any]):
        if task_id in self.active_connections:
            message = json.dumps({"event": event_type, "data": payload, "timestamp": str(payload.get("timestamp", ""))})
            dead_sockets = []
            for ws in self.active_connections[task_id]:
                try:
                    await ws.send_text(message)
                except Exception:
                    dead_sockets.append(ws)

            for ws in dead_sockets:
                self.disconnect(task_id, ws)


ws_manager = ConnectionManager()
