---
tags: [postgresql, advanced, optimization, query-rewrite]
---

# Query Optimization

## Common Optimization Patterns

### 1. Replace NOT IN with NOT EXISTS

```sql
-- Slow (NOT IN with NULLs is problematic)
SELECT * FROM users WHERE id NOT IN (SELECT user_id FROM orders);

-- Faster and correct
SELECT * FROM users u WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);
```

### 2. Replace subqueries with JOINs

```sql
-- Slower (correlated subquery)
SELECT name, (SELECT COUNT(*) FROM orders WHERE user_id = u.id) AS cnt
FROM users u;

-- Faster (JOIN with GROUP BY)
SELECT u.name, COUNT(o.id) AS cnt
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.name;
```

### 3. Use LIMIT with ORDER BY wisely

```sql
-- If you only need the top 10, add LIMIT — the planner can use an index
SELECT * FROM products ORDER BY price DESC LIMIT 10;
```

### 4. Avoid SELECT *

```sql
-- Bad: fetches all columns (more I/O, memory)
SELECT * FROM users;

-- Good: fetch only what you need
SELECT id, name, email FROM users;
```

### 5. Use covering indexes

```sql
-- Index that covers all columns the query needs → index-only scan
CREATE INDEX idx_orders_cust ON orders(customer_id) INCLUDE (total_amount, status);

-- This query can be answered entirely from the index
SELECT customer_id, total_amount, status FROM orders WHERE customer_id = 42;
```

### 6. Batch INSERTs

```sql
-- Slow: one row per INSERT
INSERT INTO logs (msg) VALUES ('a');
INSERT INTO logs (msg) VALUES ('b');
INSERT INTO logs (msg) VALUES ('c');

-- Fast: single multi-row INSERT
INSERT INTO logs (msg) VALUES ('a'), ('b'), ('c');

-- Fastest: COPY (for bulk loads)
COPY logs (msg) FROM '/path/to/file.csv' WITH CSV;
```

### 7. Use UNLOGGED tables for temporary data

```sql
-- UNLOGGED tables skip WAL writing — much faster for temp data
CREATE UNLOGGED TABLE temp_import (id int, data text);
-- (data is lost on crash, but writes are 2-3x faster)
```

## Next

- [[04-Advanced-Topics/03-EXPLAIN-ANALYZE|EXPLAIN ANALYZE]]
- [[04-Advanced-Topics/04-Partitioning|Partitioning]]
