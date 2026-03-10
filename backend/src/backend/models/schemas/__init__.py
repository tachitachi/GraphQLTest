from typing import Optional

from pydantic import BaseModel


class AuthorSchema(BaseModel):
    id: int
    name: str
    bio: Optional[str] = None


class BookSchema(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    author: AuthorSchema

