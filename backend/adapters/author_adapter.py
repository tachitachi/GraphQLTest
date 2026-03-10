
from typing import Any, Dict, List, Optional

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import authors, books

class AuthorNotFoundError(Exception):
    pass

async def get_authors(session: AsyncSession) -> List[Dict[str, Any]]:
    result = await session.execute(
        select(authors.c.id, authors.c.name, authors.c.bio).order_by(authors.c.id)
    )
    rows = result.all()
    return [{"id": row.id, "name": row.name, "bio": row.bio} for row in rows]