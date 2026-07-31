# 20 - Performance Tuning

> EXPLAIN ANALYZE, query optimization, configuration tuning, and parallel query.

---

## EXPLAIN

```sql
-- Basic plan
EXPLAIN SELECT * FROM employees WHERE department_id = 1;

-- Execute and show actual times
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM employees WHERE department_id = 1;

-- Verbose JSON output
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON)
SELECT e.*, d.name FROM employees e JOIN departments d ON e.department_id = d.id;
```

### Reading EXPLAIN

| Node | Description | When to Worry |
|------|-------------|---------------|
| Seq Scan | Read entire table | On large tables without WHERE |
| Index Scan | Use index + fetch rows | Normal for selective queries |
| Index Only Scan | Satisfy from index alone | **Best case** |
| Bitmap Index Scan | Build bitmap, then fetch | Good for moderate selectivity |
| Nested Loop | For each outer, scan inner | Fine with small outer + indexed inner |
| Hash Join | Build hash table, probe | Good for large joins |
| Merge Join | Sort both, merge | Good for sorted data |
| Sort | Sort rows | Watch for disk sorts |

---

## Configuration Tuning

### Memory

```conf
shared_buffers = 2GB                # 25% of RAM
effective_cache_size = 6GB          # 75% of RAM
work_mem = 16MB                     # Per operation
maintenance_work_mem = 512MB        # Maintenance ops
```

### Storage

```conf
random_page_cost = 1.1              # 1.1 SSD, 4.0 HDD
effective_io_concurrency = 200      # 200 SSD, 2 HDD
```

### Parallel Query

```conf
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4
```

### PostgreSQL 18: AIO (Async I/O)

```conf
# Automatic on Linux with io_uring support
# Up to 3x faster sequential scans on NVMe
```

---

## Query Optimization Patterns

### 1. Add Missing Indexes

```sql
-- Check for sequential scans on large tables
SELECT schemaname, relname, seq_scan, seq_tup_read
FROM pg_stat_user_tables
WHERE seq_scan > 100 AND seq_tup_read > 10000
ORDER BY seq_tup_read DESC;
```

### 2. Optimize JOINs

```sql
-- Ensure FK columns are indexed
CREATE INDEX idx_employees_dept ON employees(department_id);

-- Use appropriate JOIN type
-- Nested Loop: small outer + indexed inner
-- Hash Join: large unsorted datasets
-- Merge Join: pre-sorted data
```

### 3. Avoid N+1 Queries

```sql
-- Bad: N+1 queries in application
-- Good: Single JOIN query
SELECT u.*, o.id AS order_id, o.total
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
```

### 4. Use LIMIT Appropriately

```sql
-- For pagination, use keyset pagination on large tables
SELECT * FROM employees WHERE id > 1000 ORDER BY id LIMIT 10;
-- Instead of: OFFSET 1000 LIMIT 10 (slow on large offsets)
```

---

## Vacuum & Analyze

```sql
-- Update statistics
ANALYZE employees;

-- Vacuum dead tuples
VACUUM ANALYZE employees;

-- Full vacuum (locks table)
VACUUM FULL employees;

-- Check bloat
SELECT relname, n_live_tup, n_dead_tup,
    ROUND(n_dead_tup::NUMERIC / NULLIF(n_live_tup, 0) * 100, 2) AS dead_ratio
FROM pg_stat_user_tables WHERE n_dead_tup > 1000 ORDER BY n_dead_tup DESC;
```

---
*Previous: 19 - Monitoring | Next: 21 - Extensions & Ecosystem*
