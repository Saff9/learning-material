# 05 - Constraints & Indexes

## Constraints

Constraints enforce **data integrity** at the database level. They prevent invalid data from being inserted or updated.

### NOT NULL

Ensures a column cannot have NULL values.

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,        -- Must have a value
    description TEXT,                   -- Can be NULL
    price DECIMAL(10, 2) NOT NULL
);

-- Add NOT NULL to existing column
ALTER TABLE products ALTER COLUMN name SET NOT NULL;

-- Remove NOT NULL
ALTER TABLE products ALTER COLUMN name DROP NOT NULL;
```

### UNIQUE

Ensures all values in a column (or combination) are distinct.

```sql
-- Single column unique
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL
);

-- Multi-column unique (combination must be unique)
CREATE TABLE enrollments (
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    semester VARCHAR(20) NOT NULL,
    grade VARCHAR(2),
    UNIQUE (student_id, course_id, semester)
);

-- Named unique constraint
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    CONSTRAINT uq_email UNIQUE (email)
);

-- Add unique constraint to existing table
ALTER TABLE users ADD CONSTRAINT uq_username UNIQUE (username);

-- Drop unique constraint
ALTER TABLE users DROP CONSTRAINT uq_username;

-- Create unique index (more flexible than constraint)
CREATE UNIQUE INDEX idx_unique_email ON users(email);

-- Partial unique index (only certain rows must be unique)
CREATE UNIQUE INDEX idx_active_email ON users(email) WHERE is_active = TRUE;
```

### PRIMARY KEY

Combines `NOT NULL` and `UNIQUE`. Each table should have one.

```sql
-- Single column primary key
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Composite primary key
CREATE TABLE order_items (
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (order_id, product_id)
);

-- Named primary key
CREATE TABLE products (
    sku VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    CONSTRAINT pk_products PRIMARY KEY (sku)
);

-- Add primary key to existing table
ALTER TABLE customers ADD CONSTRAINT pk_customers PRIMARY KEY (id);

-- Note: Cannot have NULL in primary key columns
```

### FOREIGN KEY

Establishes relationships between tables.

```sql
-- Basic foreign key
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_date DATE DEFAULT CURRENT_DATE
);

-- Named foreign key with actions
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER CHECK (quantity > 0),
    CONSTRAINT fk_order_items_order 
        FOREIGN KEY (order_id) REFERENCES orders(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT fk_order_items_product 
        FOREIGN KEY (product_id) REFERENCES products(id) 
        ON DELETE RESTRICT
);

-- Add foreign key to existing table
ALTER TABLE orders 
ADD CONSTRAINT fk_orders_customer 
    FOREIGN KEY (customer_id) REFERENCES customers(id);

-- Drop foreign key
ALTER TABLE orders DROP CONSTRAINT fk_orders_customer;

-- Self-referencing foreign key (hierarchical data)
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER REFERENCES categories(id) ON DELETE CASCADE
);
```

### CHECK

Ensures values satisfy a boolean expression.

```sql
-- Simple check
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INTEGER CHECK (age >= 18),
    salary DECIMAL(10, 2) CHECK (salary > 0)
);

-- Named check constraint
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10, 2),
    discount_price DECIMAL(10, 2),
    CONSTRAINT chk_positive_price CHECK (price > 0),
    CONSTRAINT chk_valid_discount CHECK (discount_price IS NULL OR discount_price < price)
);

-- Complex check with multiple columns
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    CONSTRAINT chk_valid_dates CHECK (end_date >= start_date)
);

-- Add check constraint
ALTER TABLE employees ADD CONSTRAINT chk_age CHECK (age >= 18 AND age <= 100);

-- Validate existing data when adding constraint
ALTER TABLE employees ADD CONSTRAINT chk_email_format 
    CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') 
    NOT VALID;  -- Don't validate existing rows
-- Then later:
ALTER TABLE employees VALIDATE CONSTRAINT chk_email_format;

-- Drop check constraint
ALTER TABLE employees DROP CONSTRAINT chk_age;
```

### DEFAULT

Sets a default value when none is provided.

```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    view_count INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT FALSE
);

-- Add default to existing column
ALTER TABLE posts ALTER COLUMN status SET DEFAULT 'draft';

-- Remove default
ALTER TABLE posts ALTER COLUMN status DROP DEFAULT;

-- Default with expression
CREATE TABLE tasks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    due_date DATE DEFAULT CURRENT_DATE + INTERVAL '7 days'
);
```

### EXCLUSION

Prevents overlapping ranges or conflicting values (requires btree_gist extension).

```sql
-- Install extension
CREATE EXTENSION IF NOT EXISTS btree_gist;

-- Prevent overlapping room reservations
CREATE TABLE room_reservations (
    room_id INTEGER NOT NULL,
    during TSRANGE NOT NULL,
    EXCLUDE USING gist (room_id WITH =, during WITH &&)
);

-- This prevents two reservations for the same room with overlapping times
INSERT INTO room_reservations VALUES (1, '[2024-07-01 10:00, 2024-07-01 12:00)');
INSERT INTO room_reservations VALUES (1, '[2024-07-01 11:00, 2024-07-01 13:00)'); -- ERROR!
INSERT INTO room_reservations VALUES (2, '[2024-07-01 11:00, 2024-07-01 13:00)'); -- OK, different room
```

---

## Indexes

Indexes speed up queries but slow down writes. They are critical for performance.

### How Indexes Work

```
Without Index (Sequential Scan):
┌─────────────────────────────────────────────┐
│ Table: employees                            │
│ ┌────┬──────────┬─────────┐                 │
│ │ id │ name     │ salary  │                 │
│ ├────┼──────────┼─────────┤                 │
│ │ 1  │ Alice    │ 50000   │ ← Scan          │
│ │ 2  │ Bob      │ 60000   │ ← Scan          │
│ │ 3  │ Carol    │ 70000   │ ← Scan          │
│ │ 4  │ David    │ 80000   │ ← Match!        │
│ │ 5  │ Eve      │ 55000   │                 │
│ │... │ ...      │ ...     │                 │
│ └────┴──────────┴─────────┘                 │
│ O(n) - must check every row                 │
└─────────────────────────────────────────────┘

With Index (Index Scan):
┌─────────────────────────────────────────────┐
│ Index on salary (B-tree)                    │
│ ┌─────────┬──────────┐                     │
│ │ salary  │ row_id   │                     │
│ ├─────────┼──────────┤                     │
│ │ 50000   │ → id=1   │                     │
│ │ 55000   │ → id=5   │                     │
│ │ 60000   │ → id=2   │                     │
│ │ 70000   │ → id=3   │                     │
│ │ 80000   │ → id=4   │ ← Found directly!   │
│ └─────────┴──────────┘                     │
│ O(log n) - tree traversal                   │
└─────────────────────────────────────────────┘
```

### B-tree Index (Default)

Best for equality and range queries.

```sql
-- Basic index
CREATE INDEX idx_employees_name ON employees(last_name);

-- Multi-column index
CREATE INDEX idx_employees_name_dept ON employees(last_name, department_id);
-- Use when queries filter on last_name, or last_name + department_id

-- Unique index
CREATE UNIQUE INDEX idx_employees_email ON employees(email);

-- Index with condition (partial index)
CREATE INDEX idx_employees_active ON employees(last_name) WHERE is_active = TRUE;
-- Only indexes active employees, smaller and faster

-- Index with expression
CREATE INDEX idx_employees_lower_email ON employees(LOWER(email));
-- Supports case-insensitive searches: WHERE LOWER(email) = 'alice@example.com'

-- Index with sort order
CREATE INDEX idx_employees_salary_desc ON employees(salary DESC);

-- Named index
CREATE INDEX idx_employees_hire_date ON employees USING btree(hire_date);
```

### Hash Index

Best for equality comparisons only. Faster than B-tree for `=` but can't do ranges.

```sql
CREATE INDEX idx_employees_email_hash ON employees USING hash(email);
-- Only useful for: WHERE email = 'exact@match.com'
-- Cannot use for: WHERE email > 'a' (range queries)
```

### GiST Index (Generalized Search Tree)

For complex data types: geometric, range, full-text search.

```sql
-- Geospatial data (requires PostGIS, but GiST is the base)
CREATE INDEX idx_locations_point ON locations USING gist(point_column);

-- Range data
CREATE INDEX idx_reservations_during ON room_reservations USING gist(during);

-- Full-text search
CREATE INDEX idx_posts_content ON posts USING gist(to_tsvector('english', content));
```

### GIN Index (Generalized Inverted Index)

Best for composite values: arrays, JSONB, full-text search.

```sql
-- Array contains queries
CREATE INDEX idx_posts_tags ON posts USING gin(tags);
-- Supports: WHERE tags @> ARRAY['python', 'database']

-- JSONB queries
CREATE INDEX idx_products_data ON products USING gin(data);
-- Supports: WHERE data @> '{"category": "electronics"}'

-- Full-text search (better than GiST for read-heavy)
CREATE INDEX idx_posts_fts ON posts USING gin(to_tsvector('english', content));

-- GIN with specific JSONB paths
CREATE INDEX idx_products_category ON products USING gin((data -> 'category'));
```

### BRIN Index (Block Range Index)

For very large, naturally ordered tables. Very small index size.

```sql
-- Time-series data (naturally ordered by timestamp)
CREATE INDEX idx_events_created ON events USING brin(created_at);
-- 10TB table might have a BRIN index of just a few KB
-- Best for: WHERE created_at > '2024-01-01' on append-only tables
```

### SP-GiST Index

For data with natural clustering (IP addresses, phone numbers).

```sql
CREATE INDEX idx_networks ON networks USING spgist(ip_address);
```

### Index Types Comparison

| Index Type | Best For | Supports | Size |
|------------|----------|----------|------|
| **B-tree** | General purpose | `=`, `<`, `>`, `LIKE` | Medium |
| **Hash** | Exact match only | `=` only | Small |
| **GiST** | Geometric, ranges, FTS | Complex operators | Large |
| **GIN** | Arrays, JSONB, FTS | `@>`, `?`, `?&` | Very Large |
| **BRIN** | Large ordered tables | Range scans | Tiny |
| **SP-GiST** | Clustered data | Prefix/suffix match | Medium |

---

## Advanced Index Features

### Covering Indexes (INCLUDE)

Include additional columns in the index to avoid table lookups.

```sql
-- Index with included columns (PostgreSQL 11+)
CREATE INDEX idx_employees_dept_salary ON employees(department_id) INCLUDE (salary, last_name);
-- Query: SELECT salary, last_name FROM employees WHERE department_id = 1
-- The index alone can satisfy this query (Index Only Scan)
```

### Concurrent Index Creation

Create indexes without locking the table.

```sql
-- Standard CREATE INDEX blocks writes
CREATE INDEX idx_employees_name ON employees(name);

-- Concurrent creation (no locks, but slower)
CREATE INDEX CONCURRENTLY idx_employees_name ON employees(name);
-- Safe for production, but cannot run inside a transaction
```

### Index Maintenance

```sql
-- Check index usage
SELECT 
    schemaname, tablename, indexname, 
    idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename = 'employees';

-- Check index sizes
SELECT 
    schemaname, tablename, indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;

-- Reindex (rebuild index)
REINDEX INDEX idx_employees_name;
REINDEX TABLE employees;  -- Rebuild all indexes on table
REINDEX INDEX CONCURRENTLY idx_employees_name;  -- No locks

-- Analyze table (update statistics)
ANALYZE employees;

-- Remove unused indexes
-- Check idx_scan = 0 in pg_stat_user_indexes
```

### Index-Only Scans

```sql
-- Create a covering index
CREATE INDEX idx_employees_covering ON employees(department_id, last_name, salary);

-- This query can use Index Only Scan (no table access)
SELECT last_name, salary FROM employees WHERE department_id = 1;

-- Force index-only scan (for testing)
SET enable_seqscan = off;
EXPLAIN ANALYZE SELECT last_name, salary FROM employees WHERE department_id = 1;
SET enable_seqscan = on;
```

---

## Constraint vs Index Relationship

```sql
-- PRIMARY KEY automatically creates a unique index
CREATE TABLE test_pk (
    id SERIAL PRIMARY KEY
);
-- Automatically creates: UNIQUE INDEX test_pk_pkey ON test_pk(id)

-- UNIQUE constraint automatically creates a unique index
CREATE TABLE test_uq (
    email VARCHAR(100) UNIQUE
);
-- Automatically creates: UNIQUE INDEX test_uq_email ON test_uq(email)

-- FOREIGN KEY does NOT create an index automatically
-- But you should create one for the referencing column!
CREATE TABLE test_fk (
    parent_id INTEGER REFERENCES test_pk(id)
);
-- Manually create index for JOIN performance:
CREATE INDEX idx_test_fk_parent ON test_fk(parent_id);
```

---

## Best Practices

### When to Create Indexes

1. **Primary keys and unique columns** — Always
2. **Foreign keys** — Always (for JOIN performance)
3. **Frequently queried columns** — WHERE, JOIN, ORDER BY
4. **Columns used in range queries** — `>`, `<`, `BETWEEN`
5. **Text search columns** — Full-text search
6. **JSONB/array columns** — For containment queries

### When NOT to Create Indexes

1. **Small tables** — Sequential scan is often faster
2. **Frequently updated columns** — Index maintenance overhead
3. **Columns with few distinct values** — Low selectivity
4. **Columns rarely queried** — Wasted space and write overhead

### Index Design Checklist

```sql
-- 1. Check query patterns
EXPLAIN ANALYZE SELECT * FROM employees WHERE department_id = 1 AND salary > 50000;

-- 2. Create composite index matching WHERE clause order
CREATE INDEX idx_employees_dept_salary ON employees(department_id, salary);

-- 3. Verify index is used
EXPLAIN ANALYZE SELECT * FROM employees WHERE department_id = 1 AND salary > 50000;
-- Look for "Index Scan" or "Bitmap Index Scan"

-- 4. Monitor index usage over time
SELECT indexrelname, idx_scan, idx_tup_read 
FROM pg_stat_user_indexes 
WHERE relname = 'employees';

-- 5. Drop unused indexes
DROP INDEX IF EXISTS idx_unused_index;
```

---

## Summary

| Constraint | Purpose |
|------------|---------|
| `NOT NULL` | Prevent NULL values |
| `UNIQUE` | Prevent duplicate values |
| `PRIMARY KEY` | NOT NULL + UNIQUE, identifies rows |
| `FOREIGN KEY` | Enforce referential integrity |
| `CHECK` | Validate with boolean expression |
| `DEFAULT` | Set default value |
| `EXCLUSION` | Prevent overlapping ranges |

| Index Type | Use Case |
|------------|----------|
| B-tree | General equality and range queries |
| Hash | Exact match only |
| GiST | Geometric, range, full-text |
| GIN | Arrays, JSONB, full-text (read-heavy) |
| BRIN | Very large, naturally ordered tables |
| SP-GiST | Clustered data (IP, phone) |

---
*Previous: [04 - Joins & Relationships](04-joins-relationships.md) | Next: [06 - Advanced SQL](06-advanced-sql.md)*
