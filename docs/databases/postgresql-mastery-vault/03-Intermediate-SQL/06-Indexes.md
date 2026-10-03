---
tags: [sql, intermediate, indexes, performance]
---

# Indexes

Indexes make queries fast. Without indexes, PostgreSQL must scan every row (sequential scan). With indexes, it can find rows directly.

## Creating Indexes

```sql
-- Basic B-tree index (default)
CREATE INDEX idx_users_email ON users(email);

-- Index on multiple columns
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);

-- Unique index
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);

-- Index with a condition (partial index)
CREATE INDEX idx_orders_pending ON orders(user_id) WHERE status = 'pending';

-- Index on an expression
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- Covering index (INCLUDE extra columns for index-only scans)
CREATE INDEX idx_orders_cust_date ON orders(customer_id, order_date)
    INCLUDE (total_amount, status);
```

## Index Types

| Type | Best For | Operators |
|------|----------|-----------|
| **B-tree** (default) | Equality, range, sorting | `=`, `<`, `>`, `BETWEEN`, `IN`, `IS NULL`, `LIKE 'abc%'`, `ORDER BY` |
| **Hash** | Equality only | `=` (rarely used) |
| **GIN** | Multi-valued: arrays, JSONB, full-text | `@>`, `<@`, `?`, `@@` |
| **GiST** | Spatial, overlapping ranges, full-text | `&&`, `<->`, KNN |
| **BRIN** | Huge ordered tables (time-series) | Same as B-tree, block-level |
| **SP-GiST** | Non-balanced trees (IP, prefixes) | Custom |

```sql
-- GIN index for JSONB
CREATE INDEX idx_products_attrs ON products USING GIN (attributes);

-- GIN index for full-text search
CREATE INDEX idx_posts_search ON posts USING GIN (to_tsvector('english', body));

-- GiST index for ranges (prevents overlapping bookings)
CREATE INDEX idx_bookings_during ON room_bookings USING GIST (during);

-- BRIN index for time-series (tiny size, huge tables)
CREATE INDEX idx_logs_created ON logs USING BRIN (created_at);
```

## When to Index

- **Foreign key columns** (PostgreSQL does NOT auto-index these!)
- **Columns used in WHERE clauses frequently**
- **Columns used in JOIN conditions**
- **Columns used in ORDER BY frequently**
- **Columns with unique constraints** (auto-indexed)

## When NOT to Index

- Small tables (sequential scan is faster than index lookup)
- Columns rarely used in queries
- Tables with very high write load (every index slows writes)
- Columns with low selectivity (e.g., boolean columns)

## Checking Index Usage

```sql
-- Find unused indexes (candidates for removal)
SELECT
    schemaname, relname, indexrelname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

## EXPLAIN to Verify Index Usage

```sql
-- See if a query uses an index
EXPLAIN SELECT * FROM users WHERE email = 'alice@example.com';
-- Look for "Index Scan" (uses index) vs "Seq Scan" (doesn't)
```

See [[04-Advanced-Topics/03-EXPLAIN-ANALYZE|EXPLAIN ANALYZE]] for the full guide.

## Best Practices

> [!important] Index design principles
> 1. Index foreign key columns (PostgreSQL doesn't auto-create these)
> 2. Don't over-index — each index slows writes
> 3. Use partial indexes for common filtered queries
> 4. Use covering indexes (INCLUDE) for index-only scans
> 5. Monitor with `pg_stat_user_indexes` and remove unused indexes
> 6. Always verify with `EXPLAIN ANALYZE` that indexes are actually used

## Practice

```sql
-- Create an index and verify it's used
CREATE INDEX idx_employees_department ON employees(department);

EXPLAIN SELECT * FROM employees WHERE department = 'Engineering';
-- Should show "Index Scan" instead of "Seq Scan"

-- Drop it
DROP INDEX idx_employees_department;
```

## Next

- [[03-Intermediate-SQL/07-Transactions|Transactions]]
- [[04-Advanced-Topics/03-EXPLAIN-ANALYZE|EXPLAIN ANALYZE]]
