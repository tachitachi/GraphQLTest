from typing import Optional

import strawberry
from strawberry.fastapi import GraphQLRouter

from backend.graphql.context import get_context
from backend.graphql.resolvers import (
    BookMutations,
    resolve_author,
    resolve_book,
    resolve_authors,
    resolve_books,
)
from backend.graphql.types import Author, Book


@strawberry.type
class Query:
    books: list[Book] = strawberry.field(resolver=resolve_books)
    authors: list[Author] = strawberry.field(resolver=resolve_authors)
    book: Optional[Book] = strawberry.field(resolver=resolve_book)
    author: Optional[Author] = strawberry.field(resolver=resolve_author)


@strawberry.type
class Mutation:
    @strawberry.field
    def books(self) -> BookMutations:
        return BookMutations()


schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQLRouter(schema, context_getter=get_context)

