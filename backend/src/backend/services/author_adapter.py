from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.sql import authors
from backend.services.circuit_breakers.registry import db_breaker


class AuthorNotFoundError(Exception):
    pass


@db_breaker
async def get_authors(session: AsyncSession) -> List[Dict[str, Any]]:
    result = await session.execute(
        select(authors.c.id, authors.c.name, authors.c.bio).order_by(authors.c.id)
    )
    rows = result.all()
    return [{"id": row.id, "name": row.name, "bio": row.bio} for row in rows]

