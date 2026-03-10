from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.sql import authors, books
from backend.services.circuit_breakers.registry import db_breaker
from backend.services.author_adapter import AuthorNotFoundError


@db_breaker
async def get_books(session: AsyncSession) -> List[Dict[str, Any]]:
    stmt = (
        select(
            books.c.id,
            books.c.title,
            books.c.description,
            authors.c.id.label("author_id"),
            authors.c.name.label("author_name"),
            authors.c.bio.label("author_bio"),
        )
        .select_from(books.join(authors, books.c.author_id == authors.c.id))
        .order_by(books.c.id)
    )
    result = await session.execute(stmt)
    rows = result.all()
    return [
        {
            "id": row.id,
            "title": row.title,
            "description": row.description,
            "author": {
                "id": row.author_id,
                "name": row.author_name,
                "bio": row.author_bio,
            },
        }
        for row in rows
    ]


@db_breaker
async def get_book(session: AsyncSession, id: int) -> Optional[Dict[str, Any]]:
    stmt = (
        select(
            books.c.id,
            books.c.title,
            books.c.description,
            authors.c.id.label("author_id"),
            authors.c.name.label("author_name"),
            authors.c.bio.label("author_bio"),
        )
        .select_from(books.join(authors, books.c.author_id == authors.c.id))
        .where(books.c.id == id)
    )
    result = await session.execute(stmt)
    row = result.first()
    if not row:
        return None
    return {
        "id": row.id,
        "title": row.title,
        "description": row.description,
        "author": {
            "id": row.author_id,
            "name": row.author_name,
            "bio": row.author_bio,
        },
    }


@db_breaker
async def add_book(
    session: AsyncSession, title: str, author_id: int, description: Optional[str] = None
) -> Tuple[Any, Any]:
    author_result = await session.execute(
        select(authors.c.id, authors.c.name, authors.c.bio).where(authors.c.id == author_id)
    )
    author_row = author_result.first()
    if not author_row:
        raise AuthorNotFoundError(f"Author with id {author_id} does not exist")

    insert_stmt = (
        insert(books)
        .values(title=title, description=description, author_id=author_id)
        .returning(books.c.id, books.c.title, books.c.description)
    )
    inserted = await session.execute(insert_stmt)
    inserted_row = inserted.first()
    await session.commit()

    return inserted_row, author_row

