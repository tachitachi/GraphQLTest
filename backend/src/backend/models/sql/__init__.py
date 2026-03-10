from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table, Text

metadata = MetaData()

authors = Table(
    "authors",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False),
    Column("bio", Text, nullable=True),
)

books = Table(
    "books",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(200), nullable=False),
    Column("description", Text, nullable=True),
    Column(
        "author_id",
        Integer,
        ForeignKey("authors.id", ondelete="CASCADE"),
        nullable=False,
    ),
)

