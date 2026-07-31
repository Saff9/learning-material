---
tags: [postgresql, python, psycopg2, integration]
---

# Python + psycopg2

The classic PostgreSQL driver for Python.

## Installation

```bash
pip install psycopg2-binary  # binary (no build deps)
# or
pip install psycopg2         # compiles against libpq
```

## Basic Usage

```python
import psycopg2
from psycopg2.extras import RealDictCursor

DSN = "dbname=myapp user=appuser password=secret host=localhost port=5432"

# Context managers handle commit/rollback automatically
with psycopg2.connect(DSN) as conn:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Parameterized query (prevents SQL injection!)
        cur.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id",
            ("Alice", "alice@example.com")
        )
        new_id = cur.fetchone()["id"]

        cur.execute("SELECT id, name FROM users WHERE email = %s", ("alice@example.com",))
        user = cur.fetchone()

print(f"Created user {new_id}: {user}")
```

> [!warning] Always use parameterized queries
> NEVER use Python string formatting (f-strings, .format(), %) for SQL values. This causes SQL injection. Always use `%s` placeholders with psycopg2.

## CRUD Operations

```python
# CREATE
cur.execute("INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id",
            ("Bob", "bob@example.com"))
user_id = cur.fetchone()["id"]

# READ
cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
user = cur.fetchone()

# UPDATE
cur.execute("UPDATE users SET name = %s WHERE id = %s", ("Robert", user_id))

# DELETE
cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
```

## Transactions

```python
# Manual transaction control
conn.autocommit = False  # default

try:
    with conn.cursor() as cur:
        cur.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
        cur.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
    conn.commit()
except Exception:
    conn.rollback()
    raise
```

## Context Manager Pattern (Recommended)

```python
# The 'with conn:' block auto-commits on success, auto-rolls-back on exception
with psycopg2.connect(DSN) as conn:
    with conn.cursor() as cur:
        cur.execute("INSERT INTO users (name) VALUES (%s)", ("Alice",))
        cur.execute("INSERT INTO users (name) VALUES (%s)", ("Bob",))
# Both inserts commit automatically here
```

## Next

- [[07-Application-Integration/02-Python-SQLAlchemy|SQLAlchemy]]
- [[07-Application-Integration/05-Supabase|Supabase]]
