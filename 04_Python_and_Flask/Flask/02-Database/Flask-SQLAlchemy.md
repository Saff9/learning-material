---
title: Flask-SQLAlchemy
tags:
  - flask
  - database
  - sqlalchemy
  - orm
  - models
  - querying
aliases:
  - SQLAlchemy in Flask
  - Flask ORM
  - FSA
related:
  - "[[Flask-Migrate]]"
  - "[[Flask-Login]]"
  - "[[Marshmallow]]"
  - "[[Project-Structure]]"
created: 2024-01-15
updated: 2024-01-15
---

# Flask-SQLAlchemy

#flask #database #sqlalchemy #orm #models

> [!info] The single most-used Flask extension
> Flask-SQLAlchemy (FSA) is the de facto database layer for Flask. It wraps the [SQLAlchemy](https://www.sqlalchemy.org/) ORM, providing a `db` object, a model base class, session management, and integration with Flask's request lifecycle. **If you're building a real Flask app with a database, you are almost certainly using this.**

This is the longest note in the vault because Flask-SQLAlchemy is the largest topic. Even so, it's not exhaustive — see the [SQLAlchemy documentation](https://docs.sqlalchemy.org/) for the parts we skim.

---

## 1. Overview & Metaphor

### What is an ORM?

An **ORM** (Object-Relational Mapper) translates between Python objects and database rows. Instead of writing:

```sql
INSERT INTO users (email, name) VALUES ('alice@example.com', 'Alice');
SELECT * FROM users WHERE email = 'alice@example.com';
```

You write:

```python
user = User(email="alice@example.com", name="Alice")
db.session.add(user)
db.session.commit()

from sqlalchemy import select
user = db.session.execute(select(User).filter_by(email="alice@example.com")).scalars().first()
```

The ORM generates the SQL, handles parameter binding (preventing SQL injection), converts rows to Python objects, and tracks changes so it can generate `UPDATE` statements automatically.

> [!tip] The metaphor
> An ORM is like a **simultaneous interpreter** between two languages: Python and SQL. You speak Python; it speaks SQL to the database; it translates the database's reply back to Python objects. Like any interpreter, it occasionally makes mistakes or loses nuance — which is why you sometimes need to "speak SQL directly" (raw queries).

### SQLAlchemy Core vs ORM

SQLAlchemy is actually two libraries:

| Layer | What it does | When to use |
|---|---|---|
| **Core** | SQL expression language. Tables, `select()`, `insert()`, results as tuples. | Reporting queries, bulk operations, when you want SQL control. |
| **ORM** | Maps tables to classes. `User.query.all()`, relationship traversal. | Most application code. |

Flask-SQLAlchemy exposes **both**. You can mix them freely:

```python
# ORM
from sqlalchemy import select
users = db.session.execute(select(User)).scalars().all()

# Core
from sqlalchemy import select
result = db.session.execute(select(User).where(User.email.like("%@example.com")))
users = result.scalars().all()
```

### What Flask-SQLAlchemy adds

Plain SQLAlchemy requires ~30 lines of boilerplate to set up an engine, session factory, base class, and request lifecycle hooks. FSA does that for you:

- A single `db = SQLAlchemy()` object (created with the [extensions pattern](../01-Introduction/Project-Structure.md#where-each-extension-lives))
- A `db.Model` base class that uses the same `Metadata` for all models
- A `db.session` scoped to the Flask request (auto-removed on teardown)
- A `db.engine` configured from `app.config["SQLALCHEMY_DATABASE_URI"]`
- Helpers: `db.Column`, `db.String`, `db.Integer`, `db.relationship`, etc. — re-exports of SQLAlchemy constructors
- `Model.query` — a Flask-aware `Query` object (deprecated in 3.1 in favor of `db.session.execute(select(...))`)

---

## 2. Installation

```bash
(venv) $ pip install Flask-SQLAlchemy
```

Versions referenced in this note:

| Package | Version |
|---|---|
| Flask | 3.0.x |
| Flask-SQLAlchemy | 3.1.x |
| SQLAlchemy | 2.0.x |

> [!warning] Flask-SQLAlchemy 3.x is a major rewrite
> 2.x had a global `db` and a `Model.query` shortcut. 3.x removed some shortcuts, made the session explicitly scoped, and is fully SQLAlchemy 2.0-compliant. Code written for 2.x mostly works, but test before upgrading.

You'll also need a database driver:

| Database | Driver package | URI scheme |
|---|---|---|
| SQLite | built-in | `sqlite:///path.db` or `sqlite:///:memory:` |
| PostgreSQL | `psycopg2-binary` or `psycopg` (v3) | `postgresql://user:pass@host:5432/dbname` |
| MySQL | `pymysql` or `mysqlclient` | `mysql+pymysql://user:pass@host:3306/dbname` |
| MSSQL | `pyodbc` | `mssql+pyodbc://user:pass@dsn` |
| Oracle | `oracledb` | `oracle+oracledb://user:pass@host:1522/?service_name=XE` |

```bash
(venv) $ pip install Flask-SQLAlchemy psycopg2-binary  # for Postgres
```

---

## 3. Configuration

### Minimal config

```python
# app/extensions.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

```python
# app/__init__.py
from flask import Flask
from app.extensions import db

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app
```

### All configuration options

| Option | Default | Description |
|---|---|---|
| `SQLALCHEMY_DATABASE_URI` | `"sqlite:///:memory:"` | Main database URI. Required. |
| `SQLALCHEMY_BINDS` | `None` | Dict of `{name: uri}` for multi-database support. |
| `SQLALCHEMY_ENGINE_OPTIONS` | `{}` | Dict passed to `create_engine()` — pool size, recycle, etc. |
| `SQLALCHEMY_ECHO` | `False` | If `True`, log every SQL statement. Dev/debug only. |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | `False` (since 3.0) | If `True`, emits a signal before every commit. Almost always leave `False`. |
| `SQLALCHEMY_RECORD_QUERIES` | `False` | If `True`, records every query for `get_debug_queries()`. Use with `flask_debugtoolbar`. |

> [!danger] `SQLALCHEMY_TRACK_MODIFICATIONS = True` is a footgun
> It enables a signal that fires on every session change. In Flask 1.x this defaulted to `True` and caused performance issues. In 3.x it defaults to `False`. If you see a warning about it, set it to `False`.

### Production-grade config

```python
# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 20,            # number of persistent connections to keep
        "max_overflow": 10,         # extra connections allowed under load
        "pool_timeout": 30,         # seconds to wait for a free connection
        "pool_recycle": 1800,       # recycle connections every 30 minutes
        "pool_pre_ping": True,      # check connection health before use
    }


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
```

> [!tip] `pool_pre_ping = True` is essential
> If your database (or a firewall between you and it) drops idle connections, SQLAlchemy will hand you a dead connection and you'll get a `OperationalError` on the next query. `pool_pre_ping` makes it test the connection before returning it from the pool. Enable this in production. Always.

### Multi-database (binds)

```python
app.config["SQLALCHEMY_BINDS"] = {
    "users":    "postgresql://user:pass@host/users",
    "analytics": "mysql+pymysql://user:pass@host/analytics",
}
```

```python
class User(db.Model):
    __bind_key__ = "users"
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    # ...

class Event(db.Model):
    __bind_key__ = "analytics"
    __tablename__ = "events"
    # ...
```

> [!note] Multi-DB caveats
> Cross-database joins are **not** supported. Transactions across databases are not atomic. Use binds when you have truly separate databases (e.g., a legacy DB you can't change), not as a "sharding" feature.

---

## 4. Basic Usage

### Defining a model

```mermaid
classDiagram
    class db_Model {
        <<SQLAlchemy base>>
        +query: Query
        +metadata: MetaData
    }
    class UserMixin {
        +is_authenticated: bool
        +is_active: bool
        +is_anonymous: bool
        +get_id() str
    }
    class User {
        +int id
        +str email
        +str username
        +str password_hash
        +datetime created_at
        +set_password(pw)
        +check_password(pw) bool
    }
    class Post {
        +int id
        +str title
        +text body
        +int author_id
        +datetime created_at
        +User author
        +list~Comment~ comments
    }
    class Comment {
        +int id
        +text body
        +int post_id
        +int author_id
        +Post post
        +User author
    }
    class Tag {
        +int id
        +str name
        +list~Post~ posts
    }

    db_Model <|-- User
    db_Model <|-- Post
    db_Model <|-- Comment
    db_Model <|-- Tag
    UserMixin <|-- User
    User "1" --> "0..*" Post : writes
    User "1" --> "0..*" Comment : writes
    Post "1" --> "0..*" Comment : has
    Post "0..*" -- "0..*" Tag : tagged_with
```

Every model inherits from `db.Model` (which is `db.Model` from Flask-SQLAlchemy, itself a subclass of SQLAlchemy’s `DeclarativeBase`). Mixins like `UserMixin` are added as additional bases to layer in behaviour without coupling to the ORM.

```python
# app/models/user.py
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column
from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(db.String(64), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active_user: Mapped[bool] = mapped_column(db.Boolean, default=True, nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"
```

### CRUD operations

```python
# CREATE
user = User(email="alice@example.com", username="alice")
user.set_password("hunter2")    # see Flask-Login note for password handling
db.session.add(user)
db.session.commit()
# user.id is now populated

# READ
user = db.session.get(User, 1)                                                           # by PK (SQLAlchemy 2.0)
user = db.session.execute(db.select(User).filter_by(username="alice")).scalars().first() # by attribute

# UPDATE
user.email = "alice@newdomain.com"
db.session.commit()  # SQLAlchemy auto-detects the change

# DELETE
db.session.delete(user)
db.session.commit()
```

### The session in detail

The `db.session` is a **Unit of Work** — it tracks every object you've touched and figures out the right SQL to emit on `commit()`.

```python
u1 = User(username="alice")
u2 = User(username="bob")

db.session.add(u1)
db.session.add(u2)

u1.username = "alice_smith"   # before commit — SQLAlchemy remembers this

db.session.commit()
# INSERT INTO users (username) VALUES ('alice_smith'), ('bob');
```

#### Rollbacks

```python
try:
    db.session.add(User(email="duplicate@example.com"))
    db.session.commit()
except db.IntegrityError:
    db.session.rollback()  # CRITICAL: clear the failed transaction
    raise
```

> [!warning] Always rollback on error
> After any exception during `commit()`, the session is in a broken state. **You must call `db.session.rollback()`** before using it again, or every subsequent operation will raise `PendingRollbackError`.

#### `flush` vs `commit`

- `db.session.flush()` — sends SQL to the database but doesn't commit. Useful for getting auto-generated IDs without committing.
- `db.session.commit()` — flush + actually commit the transaction.

```python
user = User(username="alice")
db.session.add(user)
db.session.flush()
print(user.id)  # available now, but not committed
# ... maybe more work ...
db.session.commit()
```

```mermaid
stateDiagram-v2
    [*] --> Detached: object created, not in session
    Detached --> Pending: db.session.add\(obj\)
    Pending --> Persistent: db.session.flush\(\)\nor db.session.commit\(\)
    Persistent --> Persistent: attribute changes tracked\n(UPDATE queued on next flush)
    Persistent --> Detached: db.session.expunge\(obj\)\nor session removed
    Persistent --> Deleted: db.session.delete\(obj\)
    Deleted --> Transient: db.session.commit\(\)\nor db.session.rollback\(\)
    Transient --> [*]: garbage collected
    Pending --> Detached: db.session.rollback\(\)
    Persistent --> Detached: db.session.rollback\(\)\n(removes uncommitted changes)

    note right of Persistent
        Only in this state will
        attribute mutations be
        tracked and turned into SQL.
    end note
    note right of Deleted
        Object is marked for DELETE
        but still has a session;
        commit\(\) actually removes it.
    end note
```

The four classic ORM states — **transient**, **pending**, **persistent**, **detached** — explain most “why doesn’t my change save?” bugs.

---

## 5. Relationships

### One-to-many

```python
# app/models/post.py
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from app.extensions import db

class Post(db.Model):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(db.String(200), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(db.Text)
    author_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)

    author: Mapped["User"] = db.relationship(back_populates="posts")
```

```python
# update User model:
class User(UserMixin, db.Model):
    # ... existing columns ...
    posts: Mapped[list["Post"]] = db.relationship(back_populates="author", lazy="dynamic")
```

```python
post = Post(title="Hello", body="World", author=user)
db.session.add(post)
db.session.commit()

# Usage:
for post in user.posts:        # uses lazy="dynamic" — returns a Query
    print(post.title)

user.posts.count()             # SELECT COUNT(*) FROM posts WHERE author_id=?
user.posts.filter_by(title="Hello").first()
```

### `lazy` loading strategies

| `lazy=` | Behavior | When to use |
|---|---|---|
| `"select"` (default) | Loads the relationship in a separate query when first accessed. | Default. |
| `"joined"` | Eager-loads via JOIN in the same query. | Always need the related data; one-to-one. |
| `"subquery"` | Eager-loads via a subquery. | Lists with many related objects. |
| `"selectin"` | Eager-loads via `IN (...)` (often fastest). | Lists — usually better than `subquery`. |
| `"dynamic"` | Returns a `Query` object instead of loading. | Filter/count without loading all rows. |
| `"noload"` | Never loads; returns `None`/empty. | Disabled in tests. |
| `"raise"` | Raises if accessed (forces explicit eager loading). | N+1 prevention in APIs. |

```mermaid
mindmap
  root((Relationship loading))
    lazy default
      extra query on access
      simple, predictable
      can cause N+1
    eager strategies
      joinedload
        one JOIN, dedup with .unique\(\)
        best for to-one
      selectinload
        second query with IN
        best for to-many lists
      subqueryload
        second query with subselect
        older; prefer selectinload
    lazy dynamic
        returns Query, not list
        filter / count without load
    guards
      lazy raise
        forces explicit eager load
        great in API hot paths
      lazy noload
        returns None / empty
        useful in tests
```

### Many-to-many

```python
# Association table
post_tags = db.Table(
    "post_tags",
    db.Column("post_id", db.Integer, db.ForeignKey("posts.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)


class Tag(db.Model):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(50), unique=True, nullable=False)


class Post(db.Model):
    # ... existing columns ...
    tags: Mapped[list["Tag"]] = db.relationship(secondary=post_tags, backref="posts")
```

```python
python_tag = Tag(name="python")
flask_tag = Tag(name="flask")

post = Post(title="Flask intro", body="...", author=user)
post.tags.extend([python_tag, flask_tag])

db.session.add_all([python_tag, flask_tag, post])
db.session.commit()

# Query
for tag in post.tags:
    print(tag.name)  # python, flask

# Reverse
for p in flask_tag.posts:
    print(p.title)
```

### Many-to-many with extra attributes

If you need metadata on the association (e.g., `tagged_at`), use an **association object**:

```python
class PostTag(db.Model):
    __tablename__ = "post_tags"
    post_id: Mapped[int] = mapped_column(db.ForeignKey("posts.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(db.ForeignKey("tags.id"), primary_key=True)
    tagged_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)

    post: Mapped["Post"] = db.relationship("Post", back_populates="post_tags")
    tag: Mapped["Tag"] = db.relationship("Tag", back_populates="post_tags")


class Post(db.Model):
    # ...
    post_tags = db.relationship("PostTag", back_populates="post")

    @property
    def tags(self):
        return [pt.tag for pt in self.post_tags]
```

### One-to-one

```python
class UserProfile(db.Model):
    __tablename__ = "user_profiles"
    user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), primary_key=True)
    bio: Mapped[str | None] = mapped_column(db.Text)
    avatar_url: Mapped[str | None] = mapped_column(db.String(500))

    user: Mapped["User"] = db.relationship("User", back_populates="profile", uselist=False)


class User(db.Model):
    # ...
    profile = db.relationship("UserProfile", back_populates="user", uselist=False)
```

The `uselist=False` is what makes it one-to-one instead of one-to-many.

---

## 6. Querying

### SQLAlchemy 2.0 style (recommended)

```python
from sqlalchemy import select

# All users
stmt = select(User).order_by(User.username)
users = db.session.execute(stmt).scalars().all()

# Filter
stmt = select(User).where(User.email.like("%@example.com"))
users = db.session.execute(stmt).scalars().all()

# Single
stmt = select(User).where(User.username == "alice")
user = db.session.execute(stmt).scalar_one_or_none()

# Count
from sqlalchemy import func
stmt = select(func.count()).select_from(User).where(User.is_active_user == True)
count = db.session.execute(stmt).scalar()
```

### Legacy `Query` API (still works)

```python
User.query.all()
User.query.filter_by(username="alice").first()
User.query.filter(User.email.like("%@example.com")).all()
User.query.order_by(User.username.desc()).limit(10).all()
User.query.count()
User.query.filter(User.id.in_([1, 2, 3])).all()
```

### Filters

```python
# Equality
User.query.filter(User.username == "alice")
# Inequality
User.query.filter(User.username != "alice")
# LIKE
User.query.filter(User.email.like("%@example.com"))
# ILIKE (case-insensitive, Postgres/SQLite)
User.query.filter(User.email.ilike("%@EXAMPLE.COM"))
# IN
User.query.filter(User.id.in_([1, 2, 3]))
# NOT IN
User.query.filter(~User.id.in_([1, 2, 3]))
# IS NULL
User.query.filter(User.deleted_at.is_(None))
# IS NOT NULL
User.query.filter(User.deleted_at.isnot(None))
# Between
Post.query.filter(Post.created_at.between("2024-01-01", "2024-12-31"))
# AND
User.query.filter(User.is_active_user == True, User.email.like("%@example.com"))
# OR
from sqlalchemy import or_
User.query.filter(or_(User.username == "alice", User.username == "bob"))
# String methods
User.query.filter(User.username.startswith("a"))
User.query.filter(User.username.endswith("admin"))
User.query.filter(User.username.contains("li"))
```

### Joins

```python
# Implicit via relationship
stmt = (
    select(Post)
    .join(Post.author)  # SQLAlchemy knows the join condition
    .where(User.email.like("%@example.com"))
)
posts = db.session.execute(stmt).scalars().all()

# Explicit
stmt = (
    select(Post)
    .join(User, Post.author_id == User.id)
    .where(User.is_active_user == True)
)

# Multiple columns
stmt = (
    select(User.username, func.count(Post.id).label("post_count"))
    .join(Post, Post.author_id == User.id)
    .group_by(User.id)
    .order_by(func.count(Post.id).desc())
)
rows = db.session.execute(stmt).all()
# rows is a list of Row objects: Row(username='alice', post_count=42)
for row in rows:
    print(row.username, row.post_count)
```

### Aggregations

```python
from sqlalchemy import func, desc

# Total
total = db.session.execute(select(func.count(Post.id))).scalar()

# Per-group
stmt = (
    select(User.id, User.username, func.count(Post.id).label("n"))
    .join(Post)
    .group_by(User.id)
    .having(func.count(Post.id) > 5)
    .order_by(desc("n"))
)
for row in db.session.execute(stmt):
    print(row.username, row.n)

# Min, max, avg, sum
stmt = select(
    func.min(Post.created_at),
    func.max(Post.created_at),
    func.avg(Post.id),
    func.sum(Post.view_count),
)
min_created, max_created, avg_id, total_views = db.session.execute(stmt).one()
```

### Eager loading (avoid N+1)

```mermaid
sequenceDiagram
    autonumber
    participant Code as View code
    participant Sess as db.session
    participant DB as Database
    Note over Code,DB: BAD: lazy default triggers N+1
    Code->>Sess: select(User)\n.options(none)
    Sess->>DB: SELECT * FROM users
    DB-->>Sess: 100 rows
    Sess-->>Code: 100 User objects
    loop for each user
        Code->>Sess: len(user.posts)
        Sess->>DB: SELECT * FROM posts WHERE author_id = ?
        DB-->>Sess: posts for this user
    end
    Note over Code,DB: 1 + 100 = 101 queries
    Note over Code,DB: GOOD: selectinload fixes it
    Code->>Sess: select(User)\n.options(selectinload(User.posts))
    Sess->>DB: SELECT * FROM users
    DB-->>Sess: 100 rows
    Sess->>DB: SELECT * FROM posts WHERE author_id IN \(1,2,...,100\)
    DB-->>Sess: all posts at once
    Sess-->>Code: 100 User objects with .posts populated
    Note over Code,DB: 1 + 1 = 2 queries total
```

```python
# BAD: N+1 queries (1 for users + N for each user.posts)
from sqlalchemy import select
for user in db.session.execute(select(User)).scalars().all():
    print(len(user.posts))  # separate query per user!

# GOOD: selectinload (one extra IN query for all posts)
from sqlalchemy.orm import selectinload
stmt = select(User).options(selectinload(User.posts))
for user in db.session.execute(stmt).scalars():
    print(len(user.posts))  # posts already loaded

# GOOD: joinedload (single JOIN query)
from sqlalchemy.orm import joinedload
stmt = select(User).options(joinedload(User.posts))
users = db.session.execute(stmt).scalars().unique().all()
# .unique() is required when joinedload-ing a collection (dedup parent rows)

# GOOD: lazy="raise" to make N+1 an error in dev
class User(db.Model):
    posts = db.relationship("Post", lazy="raise")
```

> [!tip] The N+1 problem
> If you ever see your API endpoint issue 100+ queries when it should issue 2, you have N+1. Use `selectinload` for collections and `joinedload` for one-to-one. The `lazy="raise"` strategy forces you to fix them in development.

---

## 7. Pagination

```python
# Manual
page = 1
per_page = 20
stmt = select(Post).order_by(Post.created_at.desc()).limit(per_page).offset((page - 1) * per_page)
posts = db.session.execute(stmt).scalars().all()

# Flask-SQLAlchemy helper (SQLAlchemy 2.0 syntax)
pagination = db.paginate(
    select(Post).order_by(Post.created_at.desc()),
    page=1, per_page=20, error_out=False
)
print(pagination.items)        # list of Post objects
print(pagination.total)        # total matching rows
print(pagination.pages)        # total pages
print(pagination.has_prev)     # True if page > 1
print(pagination.has_next)     # True if more pages
print(pagination.prev_num)
print(pagination.next_num)

# In a template
for post in pagination.items:
    ...
{% if pagination.has_prev %}
  <a href="{{ url_for('main.index', page=pagination.prev_num) }}">Prev</a>
{% endif %}
```

---

## 8. Raw SQL & Hybrid Properties

### Raw SQL via `text()`

```python
from sqlalchemy import text

stmt = text("SELECT * FROM users WHERE email LIKE :pattern")
result = db.session.execute(stmt, {"pattern": "%@example.com"})
for row in result:
    print(row.id, row.email)

# Or map to a model
stmt = text("SELECT * FROM users WHERE created_at > :since").bindparams(since="2024-01-01")
users = db.session.execute(stmt).mappings().all()  # list of dict-like
```

### Hybrid properties

A hybrid property can be used both in Python and in SQL queries:

```python
from sqlalchemy.ext.hybrid import hybrid_property


class Post(db.Model):
    # ...
    view_count: Mapped[int] = mapped_column(db.Integer, default=0)
    is_published: Mapped[bool] = mapped_column(db.Boolean, default=False)

    @hybrid_property
    def popularity(self):
        """Python-side: view_count if published, else 0."""
        return self.view_count if self.is_published else 0

    @popularity.expression
    def popularity(cls):
        """SQL-side: CASE expression."""
        from sqlalchemy import case
        return case(
            (cls.is_published == True, cls.view_count),
            else_=0,
        )


# Use in Python
post.popularity  # -> 42

# Use in SQL (!)
stmt = select(Post).order_by(Post.popularity.desc())
```

### Hybrid methods

```python
from sqlalchemy.ext.hybrid import hybrid_method

class Coordinate(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    x: Mapped[float | None] = mapped_column(db.Float)
    y: Mapped[float | None] = mapped_column(db.Float)

    @hybrid_method
    def distance(self, other_x, other_y):
        return ((self.x - other_x) ** 2 + (self.y - other_y) ** 2) ** 0.5

    @distance.expression
    def distance(cls, other_x, other_y):
        from sqlalchemy import func
        return func.sqrt((cls.x - other_x) ** 2 + (cls.y - other_y) ** 2)


# Filter in SQL
stmt = select(Coordinate).where(Coordinate.distance(0, 0) < 5)
```

---

## 9. Sessions, Transactions & Savepoints

### Nested transactions (savepoints)

```python
from sqlalchemy import begin_nested

try:
    with db.session.begin():
        user = User(username="alice")
        db.session.add(user)

        try:
            with db.session.begin_nested():  # SAVEPOINT
                risky = User(username=None)  # violates NOT NULL
                db.session.add(risky)
        except db.IntegrityError:
            # Savepoint rolled back, outer transaction still alive
            print("risky insert failed, continuing")

        # This still commits
        db.session.add(User(username="bob"))
except Exception:
    # Outer rolled back
    raise
```

### Manual session control

```python
# Sometimes you want a fresh session for batch work
from sqlalchemy.orm import Session

with Session(db.engine) as session:
    for i in range(10_000):
        session.add(LogEntry(message=f"line {i}"))
        if i % 1000 == 0:
            session.flush()  # don't accumulate 10k objects in memory
    session.commit()
```

---

## 10. Signals & Events

SQLAlchemy events fire on model operations. Useful for audit logs, search indexing, etc.

```python
from sqlalchemy import event


@event.listens_for(User, "before_insert")
def user_before_insert(mapper, connection, target):
    """Ensure usernames are lowercase before insert."""
    if target.username:
        target.username = target.username.lower()


@event.listens_for(User, "after_insert")
def user_after_insert(mapper, connection, target):
    """Emit a Celery task to send welcome email."""
    from app.tasks.emails import send_welcome_email
    send_welcome_email.delay(target.id)


@event.listens_for(Post, "before_update")
def post_before_update(mapper, connection, target):
    """Set updated_at on every update."""
    target.updated_at = datetime.utcnow()


@event.listens_for(Post, "after_delete")
def post_after_delete(mapper, connection, target):
    """Remove post from search index."""
    from app.tasks.search import unindex_post
    unindex_post.delay(target.id)
```

### Per-attribute events

```python
@event.listens_for(User.email, "set")
def user_email_set(target, value, oldvalue, initiator):
    """Lowercase email on every assignment."""
    if value:
        return value.lower()
    return value
```

> [!warning] Events can surprise you
> `before_insert` fires inside `flush()`, not `commit()`. If you raise inside an event, the whole transaction is poisoned and must be rolled back. Use sparingly.

---

## 11. Testing with SQLite In-Memory

Tests should be fast and isolated. Use SQLite in-memory + an app context per test.

```python
# tests/conftest.py
import pytest
from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope="function")
def app():
    app = create_app(testing=True)
    app.config.update(
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_ENGINE_OPTIONS={},
        TESTING=True,
        WTF_CSRF_ENABLED=False,
    )
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def db(app):
    yield _db


@pytest.fixture
def client(app):
    return app.test_client()
```

```python
# tests/test_models.py
def test_user_creation(db):
    user = User(username="alice", email="alice@example.com")
    user.set_password("hunter2")
    db.session.add(user)
    db.session.commit()

    fetched = db.session.get(User, user.id)
    assert fetched.username == "alice"
    assert fetched.check_password("hunter2")
    assert not fetched.check_password("wrong")


def test_unique_email(db):
    db.session.add(User(username="a", email="dup@example.com"))
    db.session.commit()

    db.session.add(User(username="b", email="dup@example.com"))
    with pytest.raises(db.IntegrityError):
        db.session.commit()
    db.session.rollback()
```

> [!tip] Use `pytest-flask-sqlalchemy` for transactional tests
> The [`pytest-flask-sqlalchemy`](https://pypi.org/project/pytest-flask-sqlalchemy/) plugin wraps each test in a transaction and rolls back automatically — your tests run in milliseconds and never pollute each other.

> [!warning] SQLite is not Postgres
> Tests passing on SQLite don't guarantee they pass on Postgres. Behaviors differ for: case-sensitivity in `LIKE`, JSON column operators, array columns, `ON CONFLICT` syntax, integer overflow, transaction isolation. Run a subset of tests against Postgres in CI.

---

## 12. Performance Tips

### 1. Use `pool_pre_ping`

Already covered. Always on in production.

### 2. Avoid N+1 with eager loading

Already covered. Use `selectinload` for collections.

### 3. Use `yield_per` for huge result sets

```python
# Streams results instead of loading all into memory
stmt = select(LogEntry).execution_options(yield_per=1000)
for log in db.session.execute(stmt).scalars():
    process(log)
```

### 4. Bulk operations

```python
# Bulk insert (fast — bypasses ORM events)
db.session.execute(
    User.__table__.insert(),
    [
        {"username": f"user_{i}", "email": f"user_{i}@example.com"}
        for i in range(10_000)
    ],
)
db.session.commit()
```

```python
# Bulk update via Core
from sqlalchemy import update
db.session.execute(
    update(User)
    .where(User.last_login_at < "2024-01-01")
    .values(is_active_user=False)
)
db.session.commit()
```

### 5. Disable events during bulk loads

```python
from sqlalchemy import event

# Disable audit-log events during bulk import
event.remove(User, "after_insert", user_after_insert)
try:
    # ... bulk import ...
finally:
    event.listen(User, "after_insert", user_after_insert)
```

### 6. Use `EXPLAIN`

```python
from sqlalchemy import text

result = db.session.execute(
    text("EXPLAIN ANALYZE SELECT * FROM users WHERE email LIKE 'alice%'")
)
for row in result:
    print(row)
```

### 7. Indexes

```python
class User(db.Model):
    email: Mapped[str] = mapped_column(db.String(255), unique=True, index=True)
    created_at: Mapped[datetime | None] = mapped_column(db.DateTime, index=True)

# Composite index
class Post(db.Model):
    author_id: Mapped[int | None] = mapped_column(db.ForeignKey("users.id"))
    is_published: Mapped[bool | None] = mapped_column(db.Boolean)
    created_at: Mapped[datetime | None] = mapped_column(db.DateTime)

    __table_args__ = (
        db.Index("idx_author_published", "author_id", "is_published", "created_at"),
    )
```

---

## 13. Integration with Other Extensions

### [[Flask-Login]]

Your `User` model needs `UserMixin` (for `is_authenticated`, `is_active`, `get_id`):

```python
from flask_login import UserMixin

class User(UserMixin, db.Model):
    # ...
```

See [[Flask-Login]] for the full setup.

### [[Flask-Migrate]]

Migrations read your models and generate Alembic scripts:

```bash
$ flask db init
$ flask db migrate -m "create users and posts"
$ flask db upgrade
```

See [[Flask-Migrate]].

### [[Marshmallow]] + `marshmallow-sqlalchemy`

Auto-generate schemas from models:

```python
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class PostSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        include_relationships = True
        load_instance = True

schema = PostSchema(many=True)
from sqlalchemy import select
schema.dump(db.session.execute(select(Post)).scalars().all())
```

See [[Marshmallow]].

### [[Flask-Admin]]

Auto-generate CRUD views:

```python
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

admin = Admin(app, name="Admin", template_mode="bootstrap4")
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Post, db.session))
```

See [[Flask-Admin]].

---

## 14. Full Real-World Example: A Blog

A complete, runnable blog with users, posts, comments, tags, and follow relationships.

### `app/models/user.py`

```python
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db


followers = db.Table(
    "followers",
    db.Column("follower_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("followed_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(db.String(64), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(db.String(255))
    about_me: Mapped[str | None] = mapped_column(db.String(140))
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)
    last_seen: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship("Post", back_populates="author", lazy="dynamic")
    comments = db.relationship("Comment", back_populates="author", lazy="dynamic")
    followed = db.relationship(
        "User",
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref("followers", lazy="dynamic"),
        lazy="dynamic",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        from sqlalchemy import select
        return db.session.execute(
            select(Post)
            .join(followers, (followers.c.followed_id == Post.author_id))
            .filter(followers.c.follower_id == self.id)
            .order_by(Post.created_at.desc())
        ).scalars()

    def __repr__(self):
        return f"<User {self.username}>"
```

### `app/models/post.py`

```python
from datetime import datetime
from app.extensions import db


post_tags = db.Table(
    "post_tags",
    db.Column("post_id", db.Integer, db.ForeignKey("posts.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)


class Post(db.Model):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(db.String(200), nullable=False)
    body: Mapped[str] = mapped_column(db.Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(db.String(300))
    slug: Mapped[str | None] = mapped_column(db.String(220), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime | None] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_published: Mapped[bool] = mapped_column(db.Boolean, default=False, index=True)
    view_count: Mapped[int] = mapped_column(db.Integer, default=0)

    author_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False)
    author = db.relationship("User", back_populates="posts")

    comments = db.relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    tags = db.relationship("Tag", secondary=post_tags, backref="posts")

    def __repr__(self):
        return f"<Post {self.slug}>"


class Tag(db.Model):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(50), unique=True, nullable=False, index=True)

    def __repr__(self):
        return f"<Tag {self.name}>"


class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str] = mapped_column(db.Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, index=True)
    is_approved: Mapped[bool] = mapped_column(db.Boolean, default=False)

    post_id: Mapped[int] = mapped_column(db.ForeignKey("posts.id"), nullable=False)
    post: Mapped["Post"] = db.relationship("Post", back_populates="comments")

    author_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False)
    author = db.relationship("User", back_populates="comments")
```

### ER diagram

```mermaid
erDiagram
  USER ||--o{ POST : writes
  USER ||--o{ COMMENT : writes
  POST ||--o{ COMMENT : has
  POST }o--o{ TAG : tagged_with
  USER }o--o{ USER : follows

  USER {
    int id PK
    string username UK
    string email UK
    string password_hash
    string about_me
    datetime created_at
    datetime last_seen
  }
  POST {
    int id PK
    string title
    text body
    string slug UK
    int author_id FK
    bool is_published
    int view_count
    datetime created_at
    datetime updated_at
  }
  COMMENT {
    int id PK
    text body
    int post_id FK
    int author_id FK
    bool is_approved
    datetime created_at
  }
  TAG {
    int id PK
    string name UK
  }
```

### Usage

```python
alice = User(username="alice", email="alice@example.com")
alice.set_password("secret")
bob = User(username="bob", email="bob@example.com")
bob.set_password("secret")

alice.follow(bob)

flask_tag = Tag(name="flask")
python_tag = Tag(name="python")

post = Post(
    title="Flask + SQLAlchemy",
    body="A complete example...",
    slug="flask-sqlalchemy-complete",
    author=bob,
    is_published=True,
)
post.tags.extend([flask_tag, python_tag])

db.session.add_all([alice, bob, flask_tag, python_tag, post])
db.session.commit()

# Alice's feed shows Bob's post
alice.followed_posts().all()  # -> [post]

# Add a comment
comment = Comment(body="Great post!", post=post, author=alice)
db.session.add(comment)
db.session.commit()

# Cascade delete — comments go away when post is deleted
db.session.delete(post)
db.session.commit()
from sqlalchemy import select
db.session.execute(select(Comment).filter_by(post_id=post.id)).scalars().all()  # -> []
```

---

## 15. Common Pitfalls & Troubleshooting

> [!danger] Top 10 SQLAlchemy mistakes
> 1. **Forgetting `db.session.commit()`** — your INSERTs disappear.
> 2. **Forgetting `db.session.rollback()`** after an error — every subsequent query fails.
> 3. **N+1 queries** — use `selectinload` / `joinedload`.
> 4. **Using `lazy="dynamic"` and then `.first()`** in a loop — defeats the lazy load.
> 5. **Comparing `None` with `==`** — use `.is_(None)` / `.isnot(None)`.
> 6. **Modifying a detached object** — object fetched outside an app context can't be tracked.
> 7. **Committing inside a request handler without try/except** — leaves a half-committed state on error.
> 8. **`db.session.delete(parent)` without `cascade`** — children with FKs block the delete.
> 9. **Using `func.now()` as `default`** — `default` runs in Python, not SQL. Use `server_default=func.now()`.
> 10. **Sharing a `db.session` across threads** — sessions are not thread-safe. Each thread/request gets its own.

### `PendingRollbackError`

```
sqlalchemy.exc.PendingRollbackError: This Session's transaction has been rolled back due to a previous exception during flush.
```

**Cause**: A previous query/commit raised, and you didn't rollback.

**Fix**: Always wrap writes in try/except and rollback:

```python
try:
    db.session.add(user)
    db.session.commit()
except Exception:
    db.session.rollback()
    raise
```

### `DetachedInstanceError`

```
sqlalchemy.orm.exc.DetachedInstanceError: Instance <User at 0x...> is not bound to a Session
```

**Cause**: The session that loaded the object was removed (e.g., request ended) and you tried to access a lazy attribute.

**Fix**: Either use the object within the session, or eagerly load everything you need before the session closes. Or `db.session.merge(obj)` to re-attach.

### `IntegrityError` on unique constraint

**Cause**: You tried to insert a duplicate.

**Fix**: Catch and rollback:

```python
try:
    db.session.add(User(email="dup@example.com"))
    db.session.commit()
except db.IntegrityError:
    db.session.rollback()
    return "Email already in use", 400
```

---

## 16. Best Practices

> [!tip] FSA best practices
> 1. **Always use the application factory + `extensions.py` pattern.** See [[Project-Structure]].
> 2. **One file per model domain.** `models/user.py`, `models/post.py`. Re-export from `models/__init__.py`.
> 3. **Use `db.session.commit()` sparingly.** One commit per request, at the end. SQLAlchemy figures out the order.
> 4. **Always rollback on error.** Even if you re-raise.
> 5. **Prefer `select()` over `Query`** for new code. The `Query` API is legacy.
> 6. **Use `pool_pre_ping=True`** in production.
> 7. **Index columns you filter on.** `email`, `username`, foreign keys, `created_at`.
> 8. **Use `server_default=func.now()` for timestamps**, not Python `default=datetime.utcnow` — the database is the source of truth.
> 9. **Don't put business logic in models.** Models are for data shape. Put logic in `services/`.
> 10. **Write tests against SQLite in-memory for speed**, but run a subset against Postgres in CI.

---

## 17. References & Further Reading

- [Flask-SQLAlchemy docs](https://flask-sqlalchemy.palletsprojects.com/) — the canonical reference.
- [SQLAlchemy 2.0 docs](https://docs.sqlalchemy.org/en/20/) — the underlying ORM.
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/index.html) — official walkthrough.
- [PyMySQL vs mysqlclient](https://docs.sqlalchemy.org/en/20/dialects/mysql.html) — driver choices.
- [Miguel Grinberg's Flask Mega-Tutorial: Database](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database) — pragmatic intro.
- [Talk Python To Me — SQLAlchemy episode](https://talkpython.fm/episodes/transcript/63/sqlalchemy) — interview with Mike Bayer (SQLAlchemy creator).

---

## 18. Cheat Sheet

```python
# Create
obj = Model(field="value")
db.session.add(obj)
db.session.commit()

# Read
obj = db.session.get(Model, pk)
objs = db.session.execute(select(Model)).scalars().all()
filtered = db.session.execute(
    select(Model).where(Model.field == "value")
).scalars().all()
one = db.session.execute(
    select(Model).where(Model.id == 1)
).scalar_one_or_none()

# Update
obj.field = "new"
db.session.commit()

# Delete
db.session.delete(obj)
db.session.commit()

# Filter helpers
from sqlalchemy import or_, and_, not_, func, desc, asc, case, text

# 2.0 pagination
pagination = db.paginate(select(Model), page=1, per_page=20)

# Bulk insert
db.session.execute(Model.__table__.insert(), [{...}, {...}])

# Raw SQL
db.session.execute(text("SELECT 1")).scalar()

# Eager load
from sqlalchemy.orm import selectinload, joinedload
stmt = select(User).options(selectinload(User.posts))

# Transaction
try:
    db.session.commit()
except Exception:
    db.session.rollback()
    raise
finally:
    db.session.close()  # optional; Flask teardown does this
```

---

*See also: [[Flask-Migrate]] · [[Flask-Login]] · [[Marshmallow]] · [[Flask-Admin]] · [[Project-Structure]] · [[00-Map-of-Content]]*
