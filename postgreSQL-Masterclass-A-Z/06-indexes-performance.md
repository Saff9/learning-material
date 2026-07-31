# 06 - Indexes & Performance Foundations

> Every index type, when to use each, covering indexes, partial indexes, and index maintenance.

---

## Index Types

### B-tree (Default)
Best for: equality, range, LIKE 'prefix%', ORDER BY

```sql
CREATE INDEX idx_employees_name ON employees(last_name);
CREATE INDEX idx_employees_name_first ON employees(last_name, first_name);
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- Expression index
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- Partial index (smaller, faster for common queries)
CREATE INDEX idx_active_users ON users(last_name) WHERE is_active = TRUE;

-- Include columns (covering index, PG 11+)
CREATE INDEX idx_employees_dept ON employees(department_id) INCLUDE (salary, last_name);
```

### Hash
Best for: equality only (no ranges)

```sql
CREATE INDEX idx_users_email_hash ON users USING hash(email);
-- Only supports: WHERE email = 'exact@match.com'
-- Cannot use: WHERE email > 'a'
```

### GiST (Generalized Search Tree)
Best for: geometric, range, full-text, nearest-neighbor

```sql
-- Range data
CREATE INDEX idx_reservations ON room_reservations USING gist(during);

-- Full-text search
CREATE INDEX idx_posts_fts ON posts USING gist(to_tsvector('english', content));

-- Geometric (with PostGIS)
CREATE INDEX idx_locations ON places USING gist(geom);
```

### GIN (Generalized Inverted Index)
Best for: arrays, JSONB, full-text (read-heavy)

```sql
-- Array contains
CREATE INDEX idx_posts_tags ON posts USING gin(tags);
-- WHERE tags @> ARRAY['postgresql']

-- JSONB
CREATE INDEX idx_products_data ON products USING gin(data);
-- WHERE data @> '{"category": "electronics"}'

-- Full-text (better than GiST for read-heavy)
CREATE INDEX idx_posts_fts ON posts USING gin(to_tsvector('english', content));

-- GIN with path ops (smaller, faster for @>)
CREATE INDEX idx_products_data_path ON products USING gin(data jsonb_path_ops);
```

### BRIN (Block Range Index)
Best for: very large, naturally ordered tables

```sql
-- Time-series data
CREATE INDEX idx_events_created ON events USING brin(created_at);
-- 10TB table might have a BRIN index of just a few KB
```

### SP-GiST
Best for: clustered data (IP addresses, phone numbers)

```sql
CREATE INDEX idx_networks ON networks USING spgist(ip_address);
```

---

## Index Selection Guide

| Index Type | Best For | Supports | Size |
|------------|----------|----------|------|
| B-tree | General purpose | =, <, >, LIKE prefix | Medium |
| Hash | Exact match only | = only | Small |
| GiST | Geometric, ranges, FTS | Complex ops | Large |
| GIN | Arrays, JSONB, FTS | @>, ?, ?& | Very Large |
| BRIN | Large ordered tables | Range scans | Tiny |
| SP-GiST | Clustered data | Prefix/suffix | Medium |

---

## Advanced Index Features

### Covering Indexes (INCLUDE)
```sql
CREATE INDEX idx_employees_covering ON employees(department_id) 
INCLUDE (salary, last_name, first_name);

-- Query satisfied entirely from index:
SELECT last_name, first_name, salary FROM employees WHERE department_id = 1;
-- Index Only Scan - no table access needed!
```

### Concurrent Creation
```sql
-- No table locks, safe for production
CREATE INDEX CONCURRENTLY idx_employees_name ON employees(name);
-- Cannot run inside a transaction
```

### Index Maintenance
```sql
-- Check usage
SELECT indexrelname, idx_scan, idx_tup_read 
FROM pg_stat_user_indexes WHERE relname = 'employees';

-- Check sizes
SELECT indexrelname, pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes ORDER BY pg_relation_size(indexrelid) DESC;

-- Reindex
REINDEX INDEX CONCURRENTLY idx_employees_name;

-- Analyze (update statistics)
ANALYZE employees;
```

---

## Best Practices

1. **Always index foreign keys** — critical for JOIN performance
2. **Index WHERE clause columns** — the columns you filter on
3. **Index ORDER BY columns** — prevents sorts
4. **Use partial indexes** for filtered queries — smaller and faster
5. **Use expression indexes** for computed filters — e.g., LOWER(email)
6. **Don't over-index** — each index slows down writes
7. **Monitor with pg_stat_user_indexes** — drop unused indexes
8. **Use CONCURRENTLY in production** — avoid table locks

---
*Previous: 05 - Constraints | Next: 07 - Advanced SQL*
