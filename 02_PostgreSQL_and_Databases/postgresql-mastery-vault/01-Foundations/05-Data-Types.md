---
tags: [postgresql, foundations, data-types]
---

# PostgreSQL Data Types

PostgreSQL has one of the richest type systems of any database. Understanding data types is essential for designing good schemas.

## Numeric Types

| Type | Size | Range | Use Case |
|------|------|-------|----------|
| `smallint` / `int2` | 2 bytes | -32768 to 32767 | Small lookup codes |
| `integer` / `int` / `int4` | 4 bytes | +/- 2.1 billion | Default whole-number choice |
| `bigint` / `int8` | 8 bytes | +/- 9.2 x 10^18 | Large IDs, counters |
| `numeric(p,s)` / `decimal` | variable | up to 131072 digits | **Money, financial** (exact) |
| `real` / `float4` | 4 bytes | 6 decimal digits | Scientific approximation |
| `double precision` / `float8` | 8 bytes | 15 decimal digits | Scientific approximation |
| `serial` | 4 bytes | auto-increment | Legacy auto-PK (prefer IDENTITY) |
| `bigserial` | 8 bytes | auto-increment | Legacy auto-PK (prefer IDENTITY) |

```sql
-- Use IDENTITY instead of SERIAL for auto-incrementing PKs
CREATE TABLE accounts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    balance NUMERIC(14,2) NOT NULL DEFAULT 0,  -- 14 digits, 2 decimal places
    interest_rate NUMERIC(5,4) NOT NULL DEFAULT 0.0350  -- 5 digits, 4 decimal places (e.g., 0.0350 = 3.5%)
);
```

> [!warning] Always use NUMERIC for money
> Never use `real` or `double precision` for monetary values. Floating-point rounding errors will cause incorrect calculations. Use `NUMERIC(14,2)` or similar.

## Text Types

| Type | Notes |
|------|-------|
| `text` | Variable length, no limit (~1GB). **Preferred default.** |
| `varchar(n)` | Variable length, optional max n characters |
| `char(n)` | Fixed length, blank-padded. Avoid unless legacy. |

```sql
-- In PostgreSQL, text and varchar are essentially the same performance-wise
-- Use text by default; use varchar(n) only when you have a business-logic length cap
CREATE TABLE notes (
    title VARCHAR(200),  -- limit to 200 chars
    body TEXT            -- no limit
);
```

> [!tip] Use text over varchar(n)
> In PostgreSQL, there is no performance difference between `text` and `varchar(n)`. Use `text` as the default. Use `varchar(n)` only when you have a real business reason to enforce a length limit (like a phone number field).

## Boolean

```sql
CREATE TABLE subscriptions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_trial BOOLEAN NOT NULL DEFAULT false
);

-- Accepts: true/false, t/f, 1/0, yes/no, on/off
INSERT INTO subscriptions (is_active, is_trial) VALUES (true, false);
INSERT INTO subscriptions (is_active, is_trial) VALUES ('yes', 'no');
INSERT INTO subscriptions (is_active, is_trial) VALUES (1, 0);
```

## Date and Time Types

| Type | Use Case |
|------|----------|
| `date` | Calendar date only (no time) |
| `time` | Time of day (no date) |
| `timetz` | Time of day with timezone |
| `timestamp` | Date and time (no timezone) |
| `timestamptz` | Date and time **with timezone** — **PREFERRED** |
| `interval` | Duration (e.g., '1 day 2 hours') |

```sql
CREATE TABLE events (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_date DATE NOT NULL,
    event_time TIMETZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    duration INTERVAL NOT NULL DEFAULT '1 hour'
);

INSERT INTO events (event_date, event_time, duration) VALUES
    ('2026-07-15', '14:30:00+05:30', '2 hours 30 minutes');

-- Query with date arithmetic
SELECT event_date + duration FROM events;
SELECT NOW() + INTERVAL '7 days' AS next_week;
SELECT created_at AT TIME ZONE 'Asia/Kolkata' FROM events;
```

> [!important] Always use timestamptz
> For any application that crosses timezones (which is most web apps), use `timestamptz` instead of `timestamp`. It stores the time in UTC and converts to the session timezone on display. This prevents countless timezone-related bugs.

## UUID Type

```sql
-- PostgreSQL 13+ has gen_random_uuid() built-in (no extension needed)
CREATE TABLE api_keys (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id BIGINT NOT NULL,
    key_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- PostgreSQL 18+ has UUIDv7 (timestamp-ordered, sortable)
CREATE TABLE events (
    id UUID DEFAULT uuidv7() PRIMARY KEY,
    data JSONB
);
```

> [!note] UUIDv4 vs UUIDv7
> UUIDv4 (`gen_random_uuid()`) is random — great for uniqueness, bad for index locality (random inserts cause B-tree fragmentation).
> UUIDv7 (`uuidv7()`, PostgreSQL 18+) is timestamp-ordered — sortable, index-friendly, and still globally unique. Use UUIDv7 for new projects on PostgreSQL 18+.

## JSON and JSONB

PostgreSQL's JSON support is one of its killer features. See [[04-Advanced-Topics/06-JSON-JSONB|JSON/JSONB]] for the deep dive.

| Type | Behavior |
|------|----------|
| `json` | Stored as original text, preserves whitespace/order. Slower to query. |
| `jsonb` | **Binary, decomposed** — indexable, faster querying. **Preferred.** |

```sql
CREATE TABLE products (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    attributes JSONB NOT NULL DEFAULT '{}'
);

INSERT INTO products (name, attributes) VALUES
    ('Laptop', '{"color": "silver", "ram": 16, "ssd": 512}'),
    ('Phone', '{"color": "black", "ram": 8, "storage": 128}');

-- Query JSON data
SELECT name, attributes->>'color' AS color FROM products;
SELECT name FROM products WHERE attributes @> '{"color": "silver"}';
SELECT name FROM products WHERE attributes->>'ram' = '16';
```

## Arrays

PostgreSQL can store arrays of any base type.

```sql
CREATE TABLE posts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title TEXT NOT NULL,
    tags TEXT[] NOT NULL DEFAULT '{}'
);

INSERT INTO posts (title, tags) VALUES
    ('Post 1', ARRAY['postgres', 'sql', 'tutorial']),
    ('Post 2', ARRAY['python', 'web']),
    ('Post 3', '{postgres, performance}');

-- Query arrays
SELECT * FROM posts WHERE 'postgres' = ANY(tags);
SELECT * FROM posts WHERE tags && ARRAY['python', 'rust'];  -- overlaps
SELECT title, array_length(tags, 1) AS tag_count FROM posts;
SELECT title, unnest(tags) AS tag FROM posts;  -- expand to rows
```

## Enum Types

```sql
-- Create an enum type
CREATE TYPE order_status AS ENUM (
    'pending',
    'paid',
    'shipped',
    'delivered',
    'cancelled'
);

CREATE TABLE orders (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    status order_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO orders (status) VALUES ('pending'), ('paid');

-- Enum values are ordered by definition order
SELECT * FROM orders ORDER BY status;

-- Add a new enum value (must be done with ALTER TYPE)
ALTER TYPE order_status ADD VALUE 'returned' BEFORE 'cancelled';
```

> [!warning] Enum limitations
> Enum values cannot be removed once added. Use a lookup table with a foreign key instead if you need flexibility.

## Network Address Types

| Type | Use Case |
|------|----------|
| `inet` | IPv4 or IPv6 host or network |
| `cidr` | IPv4 or IPv6 network (enforces host bits zero) |
| `macaddr` | MAC address |
| `macaddr8` | MAC address (EUI-64 format) |

```sql
CREATE TABLE access_logs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ip_address INET NOT NULL,
    accessed_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO access_logs (ip_address) VALUES
    ('192.168.1.1'),
    ('10.0.0.5'),
    ('::1');

-- Query with network operators
SELECT * FROM access_logs WHERE ip_address << '10.0.0.0/8';  -- contained in network
SELECT * FROM access_logs WHERE ip_address << '192.168.0.0/16';
```

## Range Types

Range types represent a range of values — perfect for schedules, bookings, and time periods.

| Type | Represents |
|------|-----------|
| `int4range` | Range of integers |
| `int8range` | Range of bigints |
| `numrange` | Range of numerics |
| `tsrange` | Range of timestamps |
| `tstzrange` | Range of timestamptz |
| `daterange` | Range of dates |

```sql
CREATE TABLE room_bookings (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    room_id INTEGER NOT NULL,
    during TSTZRANGE NOT NULL,
    -- Prevent double-booking with an EXCLUDE constraint
    EXCLUDE USING gist (room_id WITH =, during WITH &&)
);

INSERT INTO room_bookings (room_id, during) VALUES
    (1, '[2026-07-15 10:00+05:30, 2026-07-15 12:00+05:30)');

-- This will FAIL (overlapping booking):
-- INSERT INTO room_bookings (room_id, during) VALUES
--     (1, '[2026-07-15 11:00+05:30, 2026-07-15 13:00+05:30)');

-- Query ranges
SELECT * FROM room_bookings WHERE during @> '2026-07-15 11:00+05:30'::timestamptz;
```

## Composite Types

```sql
-- Define a composite type
CREATE TYPE address_type AS (
    street TEXT,
    city TEXT,
    zip_code TEXT,
    country TEXT
);

-- Use it in a table
CREATE TABLE customers (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    shipping_address address_type
);

INSERT INTO customers (name, shipping_address) VALUES
    ('Alice', ROW('123 Main St', 'Mumbai', '400001', 'India')),
    ('Bob', ROW('456 Oak Ave', 'Delhi', '110001', 'India'));

-- Query composite fields
SELECT name, (shipping_address).city FROM customers;
SELECT * FROM customers WHERE (shipping_address).city = 'Mumbai';
```

## Special Types

- `tsvector` / `tsquery` — full-text search (see [[04-Advanced-Topics/05-Full-Text-Search|Full-Text Search]])
- `pg_lsn` — WAL log sequence number
- `bytea` — binary data (images, files)
- `xml` — XML data (prefer JSONB)
- `money` — fixed-precision currency (prefer NUMERIC)

## Practice Exercise

Create a table that uses multiple data types:

```sql
CREATE TABLE products (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    sku TEXT NOT NULL UNIQUE,
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    weight NUMERIC(8,2)  -- in kg
);

INSERT INTO products (name, sku, price, stock, metadata, tags, weight) VALUES
    ('Laptop', 'LAP-001', 75000.00, 10, '{"brand": "Dell", "ram": 16}', ARRAY['electronics', 'computers'], 2.5),
    ('Mouse', 'MOU-001', 500.00, 100, '{"brand": "Logitech"}', ARRAY['electronics', 'accessories'], 0.15);

SELECT * FROM products;
SELECT name, price, metadata->>'brand' AS brand FROM products;
SELECT name, tags FROM products WHERE 'electronics' = ANY(tags);
```

## What's Next

- [[02-SQL-Fundamentals/01-SELECT-Basics|SELECT Basics]] — start querying your data
- [[04-Advanced-Topics/06-JSON-JSONB|JSON/JSONB deep dive]]
- [[04-Advanced-Topics/07-Arrays|Arrays deep dive]]

## External Resources

- [Official Data Types Documentation](https://www.postgresql.org/docs/current/datatype.html)
- [PostgreSQL Data Types Tutorial](https://www.postgresqltutorial.com/postgresql-data-types/)
