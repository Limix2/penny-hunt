import asyncio
import json
from fastapi import WebSocket


class Hub:
    """In-memory pub/sub for v1. Swap for Redis pub/sub to run multiple replicas."""

    def __init__(self):
        self.connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            self.connections.add(ws)

    async def disconnect(self, ws: WebSocket):
        async with self._lock:
            self.connections.discard(ws)

    async def broadcast(self, event: dict):
        msg = json.dumps(event, default=str)
        for ws in list(self.connections):
            try:
                await ws.send_text(msg)
            except Exception:
                await self.disconnect(ws)


hub = Hub()

