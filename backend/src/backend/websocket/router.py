from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.realtime.redis_pubsub_mux import RedisPubSubMultiplexer

router = APIRouter()


@router.websocket("/ws/events")
async def events_ws(ws: WebSocket) -> None:
    await ws.accept()
    subscribed: set[str] = set()
    try:
        while True:
            msg = await ws.receive_json()
            action = msg.get("action")
            event_id = msg.get("eventId")
            if not isinstance(action, str) or not isinstance(event_id, str) or not event_id:
                await ws.send_json(
                    {"type": "error", "error": "Expected {action, eventId} with non-empty strings"}
                )
                continue

            mux: RedisPubSubMultiplexer | None = getattr(ws.app.state, "mux", None)
            if mux is None:
                await ws.send_json({"type": "error", "error": "Redis is not configured on server"})
                continue

            if action == "subscribe":
                await mux.subscribe(event_id, ws)
                subscribed.add(event_id)
                await ws.send_json({"type": "subscribed", "eventId": event_id})
            elif action == "unsubscribe":
                await mux.unsubscribe(event_id, ws)
                subscribed.discard(event_id)
                await ws.send_json({"type": "unsubscribed", "eventId": event_id})
            else:
                await ws.send_json({"type": "error", "error": f"Unknown action: {action}"})
    except WebSocketDisconnect:
        pass
    finally:
        mux: RedisPubSubMultiplexer | None = getattr(ws.app.state, "mux", None)
        if mux is not None:
            for event_id in list(subscribed):
                await mux.unsubscribe(event_id, ws)

