from __future__ import annotations

import json
import logging
from typing import Any, Awaitable, Callable, Optional, TypeVar

from backend.core.config import CACHE_TTL_SECONDS

T = TypeVar("T")

logger = logging.getLogger("backend.cache")


def _ttl_seconds() -> int:
    return CACHE_TTL_SECONDS


async def cached_json(
    *,
    redis: Any,
    key: str,
    fetcher: Callable[[], Awaitable[T]],
    ttl_seconds: Optional[int] = None,
) -> T:
    """
    Redis JSON cache helper for async code.

    - Logs whether a value came from cache vs DB/fetcher.
    - Stores JSON-serializable data only.
    """
    if redis is None:
        logger.info("cache=disabled key=%s source=db", key)
        return await fetcher()

    try:
        cached_value = await redis.get(key)
    except Exception:
        logger.exception("cache=get_failed key=%s; falling back to db", key)
        cached_value = None

    if cached_value is not None:
        try:
            logger.info("cache=hit key=%s source=cache", key)
            if isinstance(cached_value, (bytes, bytearray)):
                cached_value = cached_value.decode("utf-8")
            return json.loads(cached_value)
        except Exception:
            logger.exception("cache=decode_failed key=%s; falling back to db", key)

    logger.info("cache=miss key=%s source=db", key)
    value = await fetcher()

    try:
        payload = json.dumps(value)
        ttl = _ttl_seconds() if ttl_seconds is None else max(int(ttl_seconds), 0)
        if ttl > 0:
            await redis.setex(key, ttl, payload)
        else:
            await redis.set(key, payload)
    except Exception:
        logger.exception("cache=set_failed key=%s", key)

    return value


async def cache_delete(redis: Any, *keys: str) -> None:
    if redis is None or not keys:
        return
    try:
        await redis.delete(*keys)
    except Exception:
        logger.exception("cache=delete_failed keys=%s", ",".join(keys))

