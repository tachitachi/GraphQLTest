from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set

import redis.asyncio as redis
from fastapi import WebSocket

logger = logging.getLogger(__name__)


def channel_name_for_event(event_id: str) -> str:
    return f"event:{event_id}"


@dataclass
class _EventStream:
    event_id: str
    channel: str
    pubsub: redis.client.PubSub
    task: asyncio.Task[None]
    clients: Set[WebSocket] = field(default_factory=set)


class RedisPubSubMultiplexer:
    """
    Ensures that for each event_id, we keep only one Redis PubSub subscription,
    while broadcasting messages to all connected websocket clients subscribed to that event.
    """

    def __init__(self, redis_client: redis.Redis) -> None:
        self._redis = redis_client
        self._lock = asyncio.Lock()
        self._streams: Dict[str, _EventStream] = {}

    async def aclose(self) -> None:
        async with self._lock:
            streams = list(self._streams.values())
            self._streams.clear()

        for stream in streams:
            stream.task.cancel()
            try:
                await stream.task
            except asyncio.CancelledError:
                pass
            except Exception:
                logger.exception("PubSub task error during shutdown (event_id=%s)", stream.event_id)
            try:
                await stream.pubsub.unsubscribe(stream.channel)
            except Exception:
                logger.exception("Failed to unsubscribe during shutdown (event_id=%s)", stream.event_id)
            try:
                await stream.pubsub.aclose()
            except Exception:
                logger.exception("Failed to close pubsub during shutdown (event_id=%s)", stream.event_id)

    async def subscribe(self, event_id: str, ws: WebSocket) -> None:
        async with self._lock:
            stream = self._streams.get(event_id)
            if stream is None:
                channel = channel_name_for_event(event_id)
                pubsub = self._redis.pubsub()
                await pubsub.subscribe(channel)
                task = asyncio.create_task(self._listen_loop(event_id))
                stream = _EventStream(
                    event_id=event_id,
                    channel=channel,
                    pubsub=pubsub,
                    task=task,
                )
                self._streams[event_id] = stream

            stream.clients.add(ws)

    async def unsubscribe(self, event_id: str, ws: WebSocket) -> None:
        stream: Optional[_EventStream]
        async with self._lock:
            stream = self._streams.get(event_id)
            if stream is None:
                return
            stream.clients.discard(ws)
            if stream.clients:
                return
            self._streams.pop(event_id, None)

        # Cleanup outside the lock.
        stream.task.cancel()
        try:
            await stream.task
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception("PubSub task error during cleanup (event_id=%s)", event_id)
        try:
            await stream.pubsub.unsubscribe(stream.channel)
        except Exception:
            logger.exception("Failed to unsubscribe (event_id=%s)", event_id)
        try:
            await stream.pubsub.aclose()
        except Exception:
            logger.exception("Failed to close pubsub (event_id=%s)", event_id)

    async def unsubscribe_all_for_client(self, ws: WebSocket) -> None:
        async with self._lock:
            event_ids = [eid for eid, stream in self._streams.items() if ws in stream.clients]
        for event_id in event_ids:
            await self.unsubscribe(event_id, ws)

    async def _listen_loop(self, event_id: str) -> None:
        stream = self._streams[event_id]
        try:
            async for message in stream.pubsub.listen():
                if message is None:
                    continue
                if message.get("type") != "message":
                    continue

                raw = message.get("data")
                payload: Any = raw
                if isinstance(raw, str):
                    try:
                        payload = json.loads(raw)
                    except json.JSONDecodeError:
                        payload = raw

                await self._broadcast(event_id, payload)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("PubSub listen loop crashed (event_id=%s)", event_id)

    async def _broadcast(self, event_id: str, data: Any) -> None:
        async with self._lock:
            stream = self._streams.get(event_id)
            if stream is None:
                return
            clients = list(stream.clients)

        if not clients:
            return

        msg = {"eventId": event_id, "data": data}
        dead: list[WebSocket] = []
        for ws in clients:
            try:
                await ws.send_json(msg)
            except Exception:
                dead.append(ws)

        if dead:
            async with self._lock:
                stream = self._streams.get(event_id)
                if stream is not None:
                    for ws in dead:
                        stream.clients.discard(ws)

