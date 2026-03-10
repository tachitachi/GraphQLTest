from __future__ import annotations

from typing import List, Optional

import strawberry
from graphql import GraphQLError
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.types import Info

from adapters.author_adapter import get_authors
from cache import cache_delete, cached_json
from adapters.book_adapter import AuthorNotFoundError, add_book, get_book, get_books
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


def _get_redis(info: Info):
    return info.context.get("redis")


async def resolve_books(info: Info) -> List[Book]:
    session = await _get_session(info)

    data = await cached_json(redis=_get_redis(info), key="books:all", fetcher=lambda: get_books(session))
    return [
        Book(
            id=item["id"],
            title=item["title"],
            description=item.get("description"),
            author=Author(**item["author"]),
        )
        for item in data
    ]



async def resolve_authors(info: Info) -> List[Author]:
    session = await _get_session(info)

    data = await cached_json(redis=_get_redis(info), key="authors:all", fetcher=lambda: get_authors(session))
    return [Author(**item) for item in data]


async def resolve_book(info: Info, id: int) -> Optional[Book]:
    session = await _get_session(info)
    key = f"book:{id}"

    item = await cached_json(redis=_get_redis(info), key=key, fetcher=lambda: get_book(session, id))
    if item is None:
        return None
    return Book(
        id=item["id"],
        title=item["title"],
        description=item.get("description"),
        author=Author(**item["author"]),
    )


async def resolve_author(info: Info, id: int) -> Optional[Author]:
    session = await _get_session(info)
    key = f"author:{id}"

    async def _fetch():
        result = await session.execute(
            select(authors.c.id, authors.c.name, authors.c.bio).where(authors.c.id == id)
        )
        row = result.first()
        if not row:
            return None
        return {"id": row.id, "name": row.name, "bio": row.bio}

    item = await cached_json(redis=_get_redis(info), key=key, fetcher=_fetch)
    if item is None:
        return None
    return Author(**item)


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
        try:
            inserted_row, author_row = await add_book(session, title, author_id, description)
        except AuthorNotFoundError as e:
            raise GraphQLError(str(e))

        if not inserted_row:
            raise GraphQLError("Failed to insert book")

        await cache_delete(_get_redis(info), "books:all", f"book:{inserted_row.id}")

        return Book(
            id=inserted_row.id,
            title=inserted_row.title,
            description=inserted_row.description,
            author=Author(id=author_row.id, name=author_row.name, bio=author_row.bio),
        )


schema = strawberry.Schema(query=Query, mutation=Mutation)

