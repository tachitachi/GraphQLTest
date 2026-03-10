from typing import Any, Dict

import redis.asyncio as redis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import REDIS_URL
from backend.core.database import get_session


redis_client: redis.Redis | None = None


async def init_redis_client() -> None:
    global redis_client
    if REDIS_URL and redis_client is None:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)


async def get_context(session: AsyncSession = Depends(get_session)) -> Dict[str, Any]:
    return {
        "session": session,
        "redis": redis_client,
    }

