---
tags: [postgresql, python, sqlalchemy, orm]
---

# Python + SQLAlchemy 2.0

The industry-standard Python ORM.

## Installation

```bash
pip install sqlalchemy psycopg[binary]  # psycopg3 driver
```

## Setup

```python
from sqlalchemy import create_engine, ForeignKey, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

engine = create_engine(
    "postgresql+psycopg://user:pass@localhost/myapp",
    echo=False,           # True for SQL logging
    pool_pre_ping=True    # check connection is alive before use
)

class Base(DeclarativeBase):
    pass
```

## Models

```python
class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    books: Mapped[list["Book"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped["Author"] = relationship(back_populates="books")

# Create tables
Base.metadata.create_all(engine)
```

## CRUD with Sessions

```python
# CREATE
with Session(engine) as session:
    author = Author(name="Tolkien", books=[
        Book(title="The Hobbit"),
        Book(title="LOTR")
    ])
    session.add(author)
    session.commit()

# READ
with Session(engine) as session:
    # Eager load to avoid N+1 queries
    authors = session.scalars(
        select(Author).options(selectinload(Author.books))
    ).all()

# UPDATE
with Session(engine) as session:
    author = session.get(Author, 1)
    author.name = "J.R.R. Tolkien"
    session.commit()

# DELETE
with Session(engine) as session:
    author = session.get(Author, 1)
    session.delete(author)  # cascades to books
    session.commit()
```

> [!important] Avoid the N+1 problem
> The N+1 problem: loading N related records issues 1 query for parents + N queries for children. Fix it with `selectinload` or `joinedload`:
> ```python
> # BAD: N+1 queries
> for author in session.scalars(select(Author)):
>     print(author.books)  # separate query per author
>
> # GOOD: 2 queries total
> authors = session.scalars(select(Author).options(selectinload(Author.books))).all()
> ```

## Next

- [[07-Application-Integration/03-Node-js-pg|Node.js + pg]]
- [[07-Application-Integration/04-Prisma|Prisma]]
