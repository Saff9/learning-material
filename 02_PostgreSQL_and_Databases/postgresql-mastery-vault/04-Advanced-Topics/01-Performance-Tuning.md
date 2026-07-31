---
tags: [postgresql, advanced, performance, tuning, vacuum]
---

# Performance Tuning

## VACUUM and ANALYZE

PostgreSQL uses MVCC — UPDATE/DELETE create dead tuples. VACUUM reclaims them; ANALYZE updates statistics.

```sql
-- Regular vacuum (doesn't lock, doesn't shrink files)
VACUUM (VERBOSE, ANALYZE) orders;

-- Full vacuum (locks table, reclaims space to OS) — use sparingly!
VACUUM FULL orders;

-- Analyze only (updates planner statistics)
ANALYZE orders;
```

## Autovacuum Tuning

```sql
-- Check autovacuum settings per table
SELECT relname, reloptions FROM pg_class WHERE relname = 'orders';

-- Lower the threshold for large write-heavy tables (vacuum sooner)
ALTER TABLE orders SET (autovacuum_vacuum_scale_factor = 0.05);  -- default 0.2
ALTER TABLE orders SET (autovacuum_vacuum_threshold = 1000);
```

## Memory Configuration (The Big Four)

| Parameter | Rule of Thumb | Purpose |
|-----------|--------------|---------|
| `shared_buffers` | 25% of RAM | Main cache for data pages |
| `effective_cache_size` | 75% of RAM | Planner hint (not allocated) |
| `work_mem` | 4-64 MB | Per-sort/hash (multiplies per query!) |
| `maintenance_work_mem` | 256MB-2GB | For VACUUM, CREATE INDEX |

```ini
# postgresql.conf
shared_buffers = 4GB
effective_cache_size = 12GB
work_mem = 64MB
maintenance_work_mem = 1GB
```

> [!tip] Use PGTune
> Visit [pgtune.leopard.in.ua](https://pgtune.leopard.in.ua) to generate config based on your hardware. Enter your RAM, CPU, and storage type.

## Connection Pooling with PgBouncer

PostgreSQL forks a process per connection (~5-10MB each). PgBouncer multiplexes many clients onto few backend connections.

```ini
# pgbouncer.ini (transaction mode — recommended for web apps)
[databases]
app = host=127.0.0.1 port=5432 dbname=app

[pgbouncer]
listen_port = 6432
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
```

> [!important] Always use a connection pooler in production
> For web apps, PgBouncer in transaction mode is mandatory. It prevents connection exhaustion under load.

## Identifying Slow Queries

```sql
-- Enable pg_stat_statements (in postgresql.conf)
-- shared_preload_libraries = 'pg_stat_statements'

-- Top 10 slowest queries
SELECT
    substring(query, 1, 80) AS query,
    calls,
    round(total_exec_time::numeric, 2) AS total_ms,
    round(mean_exec_time::numeric, 2) AS avg_ms,
    rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- Reset stats after tuning
SELECT pg_stat_statements_reset();
```

## Log Slow Queries

```ini
# postgresql.conf
log_min_duration_statement = 1000  # log queries > 1 second
```

## Next

- [[04-Advanced-Topics/03-EXPLAIN-ANALYZE|EXPLAIN ANALYZE]]
- [[05-Administration/05-Monitoring|Monitoring]]
