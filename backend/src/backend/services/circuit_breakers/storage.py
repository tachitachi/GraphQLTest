from __future__ import annotations

from typing import Optional

import redis
from aiobreaker.state import CircuitBreakerState
from aiobreaker.storage.redis import CircuitRedisStorage

from backend.core.config import REDIS_URL


def get_redis_client() -> Optional[redis.Redis]:
    if not REDIS_URL:
        return None
    return redis.from_url(REDIS_URL, decode_responses=False)

def create_redis_storage(name: str) -> Optional[CircuitRedisStorage]:
    client = get_redis_client()
    if client is None:
        return None
    return CircuitRedisStorage(
        state=CircuitBreakerState.CLOSED,
        redis_object=client,
        namespace=name,
    )

