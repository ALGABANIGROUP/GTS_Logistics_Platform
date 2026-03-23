from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Iterable, Optional, Set

from fastapi import WebSocket

logger = logging.getLogger("bots.ws")


class WSChannelHub:
    def __init__(self) -> None:
        self._connections: Set[WebSocket] = set()
        self._subscriptions: Dict[WebSocket, Set[str]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._connections.add(ws)
            self._subscriptions.setdefault(ws, set())

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(ws)
            self._subscriptions.pop(ws, None)
        try:
            await ws.close()
        except Exception:
            pass

    async def subscribe(self, ws: WebSocket, channel: str) -> None:
        if not channel:
            return
        async with self._lock:
            subs = self._subscriptions.setdefault(ws, set())
            subs.add(channel)

    async def unsubscribe(self, ws: WebSocket, channel: str) -> None:
        if not channel:
            return
        async with self._lock:
            subs = self._subscriptions.get(ws)
            if subs:
                subs.discard(channel)

    async def send(self, ws: WebSocket, payload: Dict[str, Any]) -> None:
        try:
            await ws.send_json(payload)
        except Exception:
            await self.disconnect(ws)

    def _match_channel(self, subscribed: Iterable[str], channel: str) -> bool:
        for sub in subscribed:
            if sub in {"*", "all"}:
                return True
            if sub == channel:
                return True
            if sub.endswith(".*") and channel.startswith(sub[:-2]):
                return True
        return False

    async def broadcast(self, channel: str, payload: Dict[str, Any]) -> None:
        message = {"type": "event", "channel": channel, "payload": payload}
        async with self._lock:
            items = [(ws, set(self._subscriptions.get(ws, set()))) for ws in self._connections]

        for ws, subs in items:
            if subs and not self._match_channel(subs, channel):
                continue
            try:
                await ws.send_json(message)
            except Exception:
                await self.disconnect(ws)


hub = WSChannelHub()


async def broadcast_event(*, channel: str, payload: Dict[str, Any]) -> None:
    if not channel:
        return
    await hub.broadcast(channel, payload)

