from __future__ import annotations

from typing import List, Optional

import strawberry
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.types import Info

from models import authors, books

@strawberry.type
class Author:
    id: int
    name: str
    bio: Optional[str]


@strawberry.type
class Book:
    id: int
    title: str
    description: Optional[str]
    author: Author


async def _get_session(info: Info) -> AsyncSession:
    return info.context["session"]


async def resolve_books(info: Info) -> List[Book]:
    session = await _get_session(info)
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
        Book(
            id=row.id,
            title=row.title,
            description=row.description,
            author=Author(
                id=row.author_id,
                name=row.author_name,
                bio=row.author_bio,
            ),
        )
        for row in rows
    ]


async def resolve_authors(info: Info) -> List[Author]:
    session = await _get_session(info)
    result = await session.execute(select(authors.c.id, authors.c.name, authors.c.bio).order_by(authors.c.id))
    rows = result.all()
    return [
        Author(
            id=row.id,
            name=row.name,
            bio=row.bio,
        )
        for row in rows
    ]


async def resolve_book(info: Info, id: int) -> Optional[Book]:
    session = await _get_session(info)
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
    return Book(
        id=row.id,
        title=row.title,
        description=row.description,
        author=Author(
            id=row.author_id,
            name=row.author_name,
            bio=row.author_bio,
        ),
    )


async def resolve_author(info: Info, id: int) -> Optional[Author]:
    session = await _get_session(info)
    result = await session.execute(
        select(authors.c.id, authors.c.name, authors.c.bio).where(authors.c.id == id)
    )
    row = result.first()
    if not row:
        return None
    return Author(id=row.id, name=row.name, bio=row.bio)


@strawberry.type
class Query:
    books: List[Book] = strawberry.field(resolver=resolve_books)
    authors: List[Author] = strawberry.field(resolver=resolve_authors)
    book: Optional[Book] = strawberry.field(resolver=resolve_book)
    author: Optional[Author] = strawberry.field(resolver=resolve_author)


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def add_book(
        self,
        info: Info,
        title: str,
        author_id: int,
        description: Optional[str] = None,
    ) -> Book:
        session = await _get_session(info)

        # Ensure author exists
        author_result = await session.execute(
            select(authors.c.id, authors.c.name, authors.c.bio).where(authors.c.id == author_id)
        )
        author_row = author_result.first()
        if not author_row:
            raise ValueError(f"Author with id {author_id} does not exist")

        insert_stmt = (
            insert(books)
            .values(title=title, description=description, author_id=author_id)
            .returning(books.c.id, books.c.title, books.c.description)
        )
        inserted = await session.execute(insert_stmt)
        inserted_row = inserted.first()
        await session.commit()
        if not inserted_row:
            raise RuntimeError("Failed to insert book")

        return Book(
            id=inserted_row.id,
            title=inserted_row.title,
            description=inserted_row.description,
            author=Author(id=author_row.id, name=author_row.name, bio=author_row.bio),
        )


schema = strawberry.Schema(query=Query, mutation=Mutation)

