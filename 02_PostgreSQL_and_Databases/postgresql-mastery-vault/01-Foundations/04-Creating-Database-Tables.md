---
tags: [postgresql, foundations, ddl, tables]
---

# Creating Databases and Tables

## Creating a Database

```sql
-- Basic database creation
CREATE DATABASE myapp;

-- With an owner
CREATE DATABASE myapp OWNER myuser;

-- With specific encoding and locale
CREATE DATABASE myapp
    ENCODING 'UTF8'
    LC_COLLATE 'en_US.UTF-8'
    LC_CTYPE 'en_US.UTF-8'
    TEMPLATE template0;

-- From a template (clone an existing database)
CREATE DATABASE myapp_copy TEMPLATE myapp;
```

### Database-level commands

```sql
-- List databases
\l

-- Connect to a database
\c myapp

-- Rename a database (must have no active connections)
ALTER DATABASE myapp RENAME TO myapp_v2;

-- Drop a database
DROP DATABASE myapp;

-- Set database-level defaults
ALTER DATABASE myapp SET timezone TO 'Asia/Kolkata';
ALTER DATABASE myapp SET work_mem TO '64MB';
```

## Creating Tables

### Basic Table Creation

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    bio TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Modern Table Creation (PostgreSQL 18+)

```sql
-- Use IDENTITY instead of SERIAL (cleaner, no orphan sequences)
CREATE TABLE users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    bio TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- With UUID v7 primary key (PostgreSQL 18+)
CREATE TABLE events (
    id UUID DEFAULT uuidv7() PRIMARY KEY,
    event_type TEXT NOT NULL,
    data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

> [!tip] IDENTITY vs SERIAL
> Prefer `GENERATED ALWAYS AS IDENTITY` over `SERIAL`. IDENTITY is SQL-standard, doesn't create orphan sequences when columns are dropped, and is cleaner. SERIAL is older PostgreSQL-specific syntax.

### Table with Foreign Keys

```sql
CREATE TABLE posts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    published BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE comments (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    body TEXT NOT NULL,
    post_id BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Table with Constraints

```sql
CREATE TABLE products (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    sku TEXT NOT NULL UNIQUE,
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    category TEXT NOT NULL CHECK (category IN ('electronics', 'clothing', 'food', 'other')),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add a comment for documentation
COMMENT ON TABLE products IS 'Product catalog with pricing and stock information';
COMMENT ON COLUMN products.sku IS 'Stock Keeping Unit - unique product identifier';
```

### Table with Generated Columns (PostgreSQL 12+)

```sql
-- Stored generated column (computed on write, can be indexed)
CREATE TABLE invoices (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    subtotal NUMERIC(10,2) NOT NULL,
    tax_rate NUMERIC(5,4) NOT NULL DEFAULT 0.18,
    tax_amount NUMERIC(10,2) GENERATED ALWAYS AS (subtotal * tax_rate) STORED,
    total NUMERIC(10,2) GENERATED ALWAYS AS (subtotal + (subtotal * tax_rate)) STORED
);

-- Virtual generated column (PostgreSQL 18+ — computed on read, cannot be indexed)
CREATE TABLE orders (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    line_total NUMERIC(10,2) GENERATED ALWAYS AS (quantity * unit_price) VIRTUAL
);
```

## Modifying Tables (ALTER TABLE)

```sql
-- Add a column
ALTER TABLE users ADD COLUMN phone TEXT;

-- Add a column with a default
ALTER TABLE users ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT false;

-- Drop a column
ALTER TABLE users DROP COLUMN phone;

-- Rename a column
ALTER TABLE users RENAME COLUMN username TO handle;

-- Change column type
ALTER TABLE users ALTER COLUMN email TYPE citext;

-- Set a default
ALTER TABLE users ALTER COLUMN is_active SET DEFAULT true;

-- Remove a default
ALTER TABLE users ALTER COLUMN is_active DROP DEFAULT;

-- Set NOT NULL
ALTER TABLE users ALTER COLUMN email SET NOT NULL;

-- Remove NOT NULL
ALTER TABLE users ALTER COLUMN bio DROP NOT NULL;

-- Add a constraint
ALTER TABLE users ADD CONSTRAINT valid_email CHECK (email LIKE '%@%');

-- Add a unique constraint
ALTER TABLE users ADD CONSTRAINT unique_phone UNIQUE (phone);

-- Drop a constraint
ALTER TABLE users DROP CONSTRAINT valid_email;
```

## Dropping Tables

```sql
-- Drop a table (fails if foreign keys reference it)
DROP TABLE users;

-- Drop with CASCADE (also drops dependent objects)
DROP TABLE users CASCADE;

-- Drop only if it exists (avoids error)
DROP TABLE IF EXISTS users;
```

## Schemas

Schemas are namespaces for tables. The default schema is `public`.

```sql
-- Create a schema
CREATE SCHEMA analytics;

-- Create a table in a specific schema
CREATE TABLE analytics.daily_stats (
    date DATE NOT NULL,
    metric TEXT NOT NULL,
    value NUMERIC NOT NULL
);

-- Set the search path (which schemas to look in)
SET search_path TO analytics, public;

-- List schemas
\dn

-- List tables in a specific schema
\dt analytics.*
```

## Naming Conventions

> [!important] PostgreSQL Naming Best Practices
> - Use **snake_case** for all identifiers (table names, column names)
> - Use **lowercase** only (PostgreSQL folds unquoted identifiers to lowercase)
> - Use **plural table names** (`users`, `posts`, `comments`) — this is the PostgreSQL community convention
> - Use **singular foreign key columns** (`user_id`, `post_id`) — references the entity
> - Use **descriptive index names**: `idx_<table>_<columns>` (e.g., `idx_users_email`)
> - Avoid reserved words (`user`, `order`, `group`) — use `users`, `orders`, `groups` instead
> - Maximum identifier length is 63 characters

## Practice Exercise

Create a schema for a simple blog:

```sql
-- Create database
CREATE DATABASE blog;
\c blog

-- Users table
CREATE TABLE users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Posts table
CREATE TABLE posts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    published BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Comments table
CREATE TABLE comments (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    body TEXT NOT NULL,
    post_id BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Insert sample data
INSERT INTO users (username, email) VALUES
    ('alice', 'alice@blog.com'),
    ('bob', 'bob@blog.com');

INSERT INTO posts (title, body, user_id, published) VALUES
    ('My First Post', 'Hello world!', 1, true),
    ('Second Post', 'More content here.', 1, true),
    ('Draft', 'This is a draft.', 2, false);

INSERT INTO comments (body, post_id, user_id) VALUES
    ('Great post!', 1, 2),
    ('Thanks for sharing.', 1, 1),
    ('Interesting thoughts.', 2, 1);

-- Verify
\dt
\d posts
SELECT * FROM posts;
SELECT * FROM comments;
```

## What's Next

- [[01-Foundations/05-Data-Types|Data Types]] — understand PostgreSQL's rich type system
- [[02-SQL-Fundamentals/01-SELECT-Basics|SELECT Basics]] — start querying

## External Resources

- [CREATE TABLE Documentation](https://www.postgresql.org/docs/current/sql-createtable.html)
- [ALTER TABLE Documentation](https://www.postgresql.org/docs/current/sql-altertable.html)
- [PostgreSQL Naming Conventions](https://www.postgresql.org/docs/current/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS)
