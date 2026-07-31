---
title: SQLAlchemy ORM
description: The complete guide to SQLAlchemy ORM — models, queries, relationships, and session management
chapter: 03-Database
tags:
  - sqlalchemy
  - orm
  - models
  - database
  - queries
  - relationships
difficulty: Intermediate
prerequisites:
  - [[03-Database/Database-Fundamentals]]
---

# SQLAlchemy ORM

> SQLAlchemy is the most powerful and widely-used database toolkit for Python. Its ORM (Object-Relational Mapper) allows you to interact with databases using Python classes and objects instead of raw SQL. Understanding SQLAlchemy deeply is one of the most valuable skills for a Flask developer.

## Learning Objectives

After completing this chapter, you will be able to:

- Explain SQLAlchemy's architecture and core components (Engine, Session, Metadata, Table, Mapper)
- Define models using declarative base and modern type-mapped declarations
- Perform CRUD operations using the ORM session
- Create and manage one-to-many, many-to-one, and many-to-many relationships
- Write efficient queries using the Select API and query optimization techniques
- Understand SQLAlchemy's session lifecycle and transaction management
- Implement database migrations with Alembic

## SQLAlchemy Architecture

SQLAlchemy consists of two main layers:

```mermaid
graph TD
    subgraph "SQLAlchemy ORM"
        ORM[ORM Layer<br/>Mapped Classes<br/>Session]
    end
    
    subgraph "SQLAlchemy Core"
        Core[Core Layer<br/>Engine<br/>Connection Pool<br/>SQL Expression Language]
    end
    
    subgraph "Database"
        DB[(PostgreSQL<br/>MySQL<br/>SQLite<br/>etc.)]
    end
    
    ORM --> Core
    Core --> DB
    
    style ORM fill:#e3f2fd
    style Core fill:#e8f5e9
    style DB fill:#fff3e0
```

### Core Components

| Component | Purpose |
|-----------|---------|
| **Engine** | Manages database connections and dialects |
| **Connection Pool** | Reuses database connections efficiently |
| **Metadata** | Collection of Table objects and schema constructs |
| **Table** | Represents a database table |
| **Mapper** | Connects a Python class to a Table |
| **Session** | ORM-level unit of work; tracks changes and commits transactions |
| **Declarative Base** | Combines Table, Mapper, and class definition into one step |

## Setting Up SQLAlchemy with Flask

### Installation

```bash
pip install Flask-SQLAlchemy
# For PostgreSQL:
pip install psycopg2-binary
# For MySQL:
pip install pymysql
# SQLite is included with Python
```

### Basic Configuration

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable overhead

db = SQLAlchemy(app)
```

### Database URI Formats

| Database | URI Format |
|----------|-----------|
| SQLite (file) | `sqlite:///path/to/app.db` |
| SQLite (memory) | `sqlite:///:memory:` |
| PostgreSQL | `postgresql://user:password@host:port/dbname` |
| MySQL | `mysql+pymysql://user:password@host:port/dbname` |

## Defining Models

### Modern Declarative Style (SQLAlchemy 2.0+)

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, ForeignKey
from datetime import datetime
from typing import Optional, List

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(default=True)
    
    # Relationship
    posts: Mapped[List['Post']] = relationship(back_populates='author')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Post(Base):
    __tablename__ = 'posts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Foreign key
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    
    # Relationship
    author: Mapped['User'] = relationship(back_populates='posts')
    
    def __repr__(self):
        return f'<Post {self.title}>'
```

### Classic Style (Pre-2.0)

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
```

> [!TIP]
> Use the modern 2.0+ style for new projects. It provides better type hints, clearer syntax, and is the recommended approach going forward.

## Column Types

| SQLAlchemy Type | Python Type | SQL Equivalent |
|----------------|-------------|----------------|
| `Integer` | `int` | `INTEGER` |
| `String(length)` | `str` | `VARCHAR(length)` |
| `Text` | `str` | `TEXT` |
| `Boolean` | `bool` | `BOOLEAN` |
| `DateTime` | `datetime` | `DATETIME` |
| `Date` | `date` | `DATE` |
| `Time` | `time` | `TIME` |
| `Float` | `float` | `FLOAT` |
| `Numeric(precision, scale)` | `Decimal` | `NUMERIC` |
| `LargeBinary` | `bytes` | `BLOB` / `BYTEA` |
| `JSON` | `dict` / `list` | `JSON` |
| `Enum` | `Enum` / `str` | `ENUM` |

## Column Options

| Option | Description |
|--------|-------------|
| `primary_key=True` | Primary key column |
| `autoincrement=True` | Auto-increment (default for integer PK) |
| `nullable=False` | NOT NULL constraint |
| `unique=True` | UNIQUE constraint |
| `default=value` | Default value |
| `index=True` | Create database index |
| `server_default=text('...')` | Database-side default |

## CRUD Operations

### Create

```python
# Create a new user
user = User(username='john_doe', email='john@example.com')
db.session.add(user)
db.session.commit()  # Must commit to persist

# Create with relationships
post = Post(title='Hello World', content='First post!', author=user)
db.session.add(post)
db.session.commit()

# Bulk create
users = [
    User(username='alice', email='alice@example.com'),
    User(username='bob', email='bob@example.com'),
]
db.session.add_all(users)
db.session.commit()
```

### Read

```python
from sqlalchemy import select

# Get by primary key
user = db.session.get(User, 1)  # Returns None if not found

# Select with filter
result = db.session.execute(select(User).where(User.username == 'john_doe'))
user = result.scalar_one_or_none()

# Select all
result = db.session.execute(select(User))
users = result.scalars().all()

# Filter with multiple conditions
from sqlalchemy import and_, or_
result = db.session.execute(
    select(User).where(
        and_(User.is_active == True, User.username.like('j%'))
    )
)

# Order by
result = db.session.execute(select(User).order_by(User.created_at.desc()))

# Limit and offset
result = db.session.execute(
    select(User).limit(10).offset(20)
)  # Page 3, 10 per page

# Count
from sqlalchemy import func
count = db.session.execute(select(func.count()).select_from(User)).scalar()
```

### Update

```python
# Modify and commit
user = db.session.get(User, 1)
user.email = 'new_email@example.com'
db.session.commit()

# Bulk update
db.session.execute(
    update(User).where(User.is_active == False).values(is_active=True)
)
db.session.commit()
```

### Delete

```python
# Delete an object
user = db.session.get(User, 1)
db.session.delete(user)
db.session.commit()

# Bulk delete
db.session.execute(delete(User).where(User.is_active == False))
db.session.commit()
```

## Relationships

### One-to-Many

```python
class Department(Base):
    __tablename__ = 'departments'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    
    employees: Mapped[List['Employee']] = relationship(back_populates='department')

class Employee(Base):
    __tablename__ = 'employees'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    dept_id: Mapped[int] = mapped_column(ForeignKey('departments.id'))
    
    department: Mapped['Department'] = relationship(back_populates='employees')
```

### Many-to-Many

```python
# Association table
post_tags = Table(
    'post_tags',
    Base.metadata,
    Column('post_id', ForeignKey('posts.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True)
)

class Post(Base):
    __tablename__ = 'posts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    
    tags: Mapped[List['Tag']] = relationship(secondary=post_tags, back_populates='posts')

class Tag(Base):
    __tablename__ = 'tags'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    
    posts: Mapped[List['Post']] = relationship(secondary=post_tags, back_populates='tags')
```

### Relationship Options

| Option | Description |
|--------|-------------|
| `back_populates` | Bidirectional relationship |
| `lazy='select'` | Load on first access (default) |
| `lazy='joined'` | Load via JOIN in same query |
| `lazy='dynamic'` | Return query object (can be filtered further) |
| `lazy='raise'` | Raise error if accessed without eager loading |
| `cascade='all, delete-orphan'` | Auto-delete children when parent is deleted |
| `uselist=False` | One-to-one relationship |

## Eager Loading

Avoid N+1 query problems with eager loading:

```python
from sqlalchemy.orm import joinedload, selectinload

# Load users with their posts in one query
result = db.session.execute(
    select(User).options(joinedload(User.posts))
)
users = result.unique().scalars().all()

# Load posts with their author
result = db.session.execute(
    select(Post).options(joinedload(Post.author))
)
posts = result.unique().scalars().all()

# For one-to-many, selectinload is often more efficient
result = db.session.execute(
    select(User).options(selectinload(User.posts))
)
```

## Query Optimization

### Only Load Needed Columns

```python
from sqlalchemy.orm import load_only

result = db.session.execute(
    select(User).options(load_only(User.username, User.email))
)
```

### Use Indexes

```python
class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), index=True)  # Index
    email: Mapped[str] = mapped_column(String(120), unique=True)   # Implicit index
```

### Batch Operations

```python
# Use yield_per for large result sets
result = db.session.execute(select(User).yield_per(100))
for user in result.scalars():
    process(user)
```

## Common Mistakes

**Mistake: Forgetting to commit**
Changes are not persisted until `db.session.commit()` is called.

**Mistake: N+1 queries**
Accessing related objects in a loop without eager loading causes extra queries.

**Mistake: Storing passwords in plain text**
Always hash passwords before storage (see [[04-Authentication/Password-Hashing]]).

**Mistake: Not handling session expiration**
Detached objects cannot be used after the session closes.

## Best Practices

- Use SQLAlchemy 2.0+ modern syntax for new projects
- Always commit or rollback transactions
- Use eager loading (`joinedload`, `selectinload`) to prevent N+1 queries
- Add indexes for frequently queried columns
- Use `db.session.get()` for primary key lookups
- Use migrations for all schema changes
- Keep transactions short — commit as soon as possible
- Use `nullable=False` for required fields

## Exercises

1. **Model Design**: Design models for a blog with users, posts, comments, and tags. Include all relationships.

2. **CRUD Operations**: Write CRUD operations for all models, including relationship handling.

3. **Query Optimization**: Write a query that loads all posts with their authors and comment counts in a single query.

4. **Migration**: Create an Alembic migration that adds a `published` column to the posts table.

## Quiz

**Question 1**: What are the two main layers of SQLAlchemy? What does each provide?

**Question 2**: How do you define a one-to-many relationship in SQLAlchemy 2.0+?

**Question 3**: What is the N+1 query problem, and how do you solve it?

**Question 4**: What is the difference between `db.session.get()` and `db.session.execute(select(...))`?

**Question 5**: When should you use `joinedload` vs `selectinload`?

## Interview Questions

1. "Explain SQLAlchemy's architecture. What is the difference between the Core and ORM layers?"

2. "How would you define a many-to-many relationship in SQLAlchemy?"

3. "What is the N+1 query problem? How would you identify and fix it?"

4. "Explain SQLAlchemy's session lifecycle. When do you commit, rollback, and close?"

5. "How would you optimize a slow SQLAlchemy query?"

6. "What is the difference between `lazy='joined'` and `lazy='select'` in relationships?"

## Related Chapters

- [[03-Database/Database-Fundamentals]] — Relational database basics
- [[03-Database/Flask-SQLAlchemy]] — Flask integration
- [[03-Database/Relationships]] — Advanced relationship patterns
- [[03-Database/SQLAlchemy-Migrations]] — Schema migrations with Alembic
- [[03-Database/Query-Optimization]] — Performance tuning

## Official Documentation References

- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)
- [SQLAlchemy Relationships](https://docs.sqlalchemy.org/en/20/orm/relationships.html)

---

*Previous: [[03-Database/Database-Fundamentals]] | Next: [[03-Database/Flask-SQLAlchemy]]*