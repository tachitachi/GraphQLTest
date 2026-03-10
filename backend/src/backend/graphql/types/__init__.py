from typing import Optional

import strawberry


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

