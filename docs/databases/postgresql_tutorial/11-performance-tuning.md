# 11 - Performance Tuning

## Query Planning and Execution

PostgreSQL uses a **cost-based optimizer** to choose the best execution plan.

### EXPLAIN

```sql
-- Basic explain (shows plan, not execution)
EXPLAIN SELECT * FROM employees WHERE department_id = 1;

-- EXPLAIN ANALYZE (actually executes and shows real times)
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM employees WHERE department_id = 1;

-- Verbose output
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON)
SELECT e.*, d.name 
FROM employees e 
JOIN departments d ON e.department_id = d.id 
WHERE e.salary > 50000;
```

### Reading EXPLAIN Output

```
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM employees WHERE id = 1;

┌──────────────────────────────────────────────────────────────┐
│ Index Scan using employees_pkey on employees                │
│   (cost=0.29..8.30 rows=1 width=72)                         │
│   Index Cond: (id = 1)                                      │
│   Buffers: shared hit=2                                     │
│ Planning Time: 0.123 ms                                       │
│ Execution Time: 0.045 ms                                    │
└──────────────────────────────────────────────────────────────┘

Cost components:
- cost=0.29..8.30  → startup_cost..total_cost (arbitrary units)
- rows=1           → estimated rows
- width=72         → estimated bytes per row
- Buffers: shared hit=2  → pages read from cache
- Planning Time    → time to generate plan
- Execution Time   → time to execute plan
```

### Common Plan Nodes

| Node | Description | When to Worry |
|------|-------------|---------------|
| **Seq Scan** | Read entire table sequentially | On large tables without WHERE |
| **Index Scan** | Use index, then fetch rows from table | Normal for selective queries |
| **Index Only Scan** | Satisfy query from index alone | Best case scenario |
| **Bitmap Index Scan** | Build bitmap from index, then fetch | Good for moderate selectivity |
| **Nested Loop** | For each outer row, scan inner | Fine with small outer, indexed inner |
| **Hash Join** | Build hash table, probe with other | Good for large joins |
| **Merge Join** | Sort both sides, merge | Good for sorted data, range joins |
| **Sort** | Sort rows in memory/disk | Watch for disk sorts |
| **Aggregate** | GROUP BY, COUNT, SUM, etc. | Hash aggregate is faster than sort |

### Fixing Slow Queries

```sql
-- Problem: Sequential scan on large table
EXPLAIN ANALYZE SELECT * FROM employees WHERE last_name = 'Smith';
-- Seq Scan on employees (cost=0.00..1234.56 rows=1 width=72)

-- Solution: Create index
CREATE INDEX idx_employees_last_name ON employees(last_name);

-- Verify fix
EXPLAIN ANALYZE SELECT * FROM employees WHERE last_name = 'Smith';
-- Index Scan using idx_employees_last_name (cost=0.29..8.30 rows=1 width=72)
```

---

## Configuration Tuning

### Memory Settings

```conf
# postgresql.conf

# Shared buffer cache (25% of RAM, max ~8GB for most systems)
shared_buffers = 2GB

# Effective cache size (OS + PG cache, ~75% of RAM)
effective_cache_size = 6GB

# Per-operation work memory (sorts, hashes, etc.)
# Default 4MB is usually too low
work_mem = 16MB

# Maintenance operations (VACUUM, CREATE INDEX, ALTER TABLE)
maintenance_work_mem = 512MB

# WAL buffers (auto-tuned usually, but can increase)
wal_buffers = 16MB
```

### Connection Settings

```conf
# Max connections (each uses memory)
max_connections = 200

# Connection pooling (use PgBouncer for more)
# PgBouncer is recommended for > 100 connections
```

### WAL and Checkpointing

```conf
# WAL level (replica for streaming replication)
wal_level = replica

# Checkpoint frequency (balance between recovery time and performance)
max_wal_size = 2GB
min_wal_size = 512MB
checkpoint_completion_target = 0.9

# WAL compression (PostgreSQL 15+)
wal_compression = on
```

### Query Planner

```conf
# Random page cost (lower for SSD, higher for HDD)
random_page_cost = 1.1    # SSD
# random_page_cost = 4    # HDD

# Effective IO concurrency (SSD can handle more)
effective_io_concurrency = 200  # SSD
# effective_io_concurrency = 2   # HDD

# Enable/disable specific plan types
enable_seqscan = on       # Usually keep on, use hints if needed
enable_indexscan = on
enable_bitmapscan = on
enable_tidscan = on
enable_nestloop = on
enable_hashjoin = on
enable_mergejoin = on
```

### Logging Slow Queries

```conf
# Log queries > 1 second
log_min_duration_statement = 1000

# Log all DDL
log_statement = 'ddl'

# Log connections/disconnections
log_connections = on
log_disconnections = on

# Log lock waits
log_lock_waits = on
deadlock_timeout = 1s
```

---

## Vacuum and Autovacuum

### Why Vacuum is Critical

```
UPDATE employees SET salary = 80000 WHERE id = 1;

Before UPDATE:
┌─────────────────────────────────────────┐
│ id │ name  │ salary │ xmin │ xmax │ t_ctid│
├────┼───────┼────────┼──────┼──────┼───────┤
│ 1  │ Alice │ 75000  │ 100  │ 0    │ (0,1) │
└─────────────────────────────────────────┘

After UPDATE (MVCC creates new version):
┌─────────────────────────────────────────┐
│ id │ name  │ salary │ xmin │ xmax │ t_ctid│
├────┼───────┼────────┼──────┼──────┼───────┤
│ 1  │ Alice │ 75000  │ 100  │ 200  │ (0,2) │  ← Dead tuple
│ 1  │ Alice │ 80000  │ 200  │ 0    │ (0,2) │  ← Live tuple
└─────────────────────────────────────────┘

VACUUM removes dead tuples and reclaims space.
```

### Manual Vacuum

```sql
-- Standard vacuum (reclaims space, doesn't shrink file)
VACUUM employees;

-- Vacuum with analyze (update statistics too)
VACUUM ANALYZE employees;

-- Full vacuum (reclaims space and shrinks file, locks table)
VACUUM FULL employees;

-- Vacuum verbose (show progress)
VACUUM (VERBOSE, ANALYZE) employees;

-- Vacuum specific columns
VACUUM (VERBOSE, ANALYZE) employees (salary, department_id);
```

### Autovacuum Configuration

```conf
# Enable autovacuum (should always be on)
autovacuum = on

# Thresholds for when to vacuum
autovacuum_vacuum_threshold = 50        -- Min dead tuples before vacuum
autovacuum_vacuum_scale_factor = 0.2    -- % of table size
autovacuum_analyze_threshold = 50
autovacuum_analyze_scale_factor = 0.1

-- Example: For 1M row table, vacuum when 50 + (0.2 * 1M) = 200,050 dead tuples

-- Tune for large tables
autovacuum_vacuum_scale_factor = 0.05   -- More aggressive for large tables
autovacuum_max_workers = 3
autovacuum_naptime = 1min

-- Cost limits (prevent vacuum from overwhelming system)
autovacuum_vacuum_cost_limit = -1       -- -1 = use vacuum_cost_limit
autovacuum_vacuum_cost_delay = 2ms
```

### Monitoring Bloat

```sql
-- Check table bloat
SELECT 
    schemaname,
    relname,
    n_live_tup,
    n_dead_tup,
    ROUND(n_dead_tup::NUMERIC / NULLIF(n_live_tup, 0) * 100, 2) AS dead_ratio,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;

-- Check index bloat (requires pgstattuple extension)
CREATE EXTENSION IF NOT EXISTS pgstattuple;
SELECT * FROM pgstattuple('employees_pkey');

-- Check table size
SELECT 
    relname,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
    pg_size_pretty(pg_relation_size(relid)) AS table_size,
    pg_size_pretty(pg_indexes_size(relid)) AS index_size
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
```

---

## Connection Pooling with PgBouncer

### Why Pool?

```
Without Pooling:
App ──► Connection 1 ──► PostgreSQL
App ──► Connection 2 ──► PostgreSQL
App ──► Connection 3 ──► PostgreSQL
... (100 connections = 100 processes)

With PgBouncer:
App ──► PgBouncer ──► PostgreSQL (10 actual connections)
App ──► PgBouncer ──► PostgreSQL
App ──► PgBouncer ──► PostgreSQL
... (100 app connections, 10 real DB connections)
```

### PgBouncer Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Session** | Connection lasts until client disconnects | Long sessions, prepared statements |
| **Transaction** | Connection returned after each transaction | Most applications (recommended) |
| **Statement** | Connection returned after each statement | Read-only, no transactions |

### Basic PgBouncer Config

```ini
; pgbouncer.ini
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
listen_port = 6432
listen_addr = 127.0.0.1
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt

pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 3
server_idle_timeout = 600
server_lifetime = 3600
```

---

## Partitioning

### Declarative Partitioning (PostgreSQL 10+)

```sql
-- Create partitioned table
CREATE TABLE measurements (
    city_id INT NOT NULL,
    logdate DATE NOT NULL,
    peaktemp INT,
    unitsales INT
) PARTITION BY RANGE (logdate);

-- Create partitions
CREATE TABLE measurements_y2024m01 PARTITION OF measurements
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE measurements_y2024m02 PARTITION OF measurements
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

CREATE TABLE measurements_y2024m03 PARTITION OF measurements
    FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');

-- Default partition (catches anything not matching)
CREATE TABLE measurements_default PARTITION OF measurements DEFAULT;

-- Insert data (automatically routed to correct partition)
INSERT INTO measurements VALUES (1, '2024-01-15', 25, 100);
-- Goes to measurements_y2024m01

-- Query (partition pruning eliminates irrelevant partitions)
SELECT * FROM measurements WHERE logdate = '2024-01-15';
-- Only scans measurements_y2024m01!

-- Add new partition
CREATE TABLE measurements_y2024m04 PARTITION OF measurements
    FOR VALUES FROM ('2024-04-01') TO ('2024-05-01');

-- Detach old partition
ALTER TABLE measurements DETACH PARTITION measurements_y2024m01;
-- Can now archive or drop the old partition
```

### List Partitioning

```sql
CREATE TABLE orders (
    order_id BIGINT,
    country_code CHAR(2),
    amount DECIMAL(10, 2)
) PARTITION BY LIST (country_code);

CREATE TABLE orders_us PARTITION OF orders FOR VALUES IN ('US');
CREATE TABLE orders_eu PARTITION OF orders FOR VALUES IN ('DE', 'FR', 'IT', 'ES');
CREATE TABLE orders_asia PARTITION OF orders FOR VALUES IN ('JP', 'CN', 'KR');
CREATE TABLE orders_other PARTITION OF orders DEFAULT;
```

### Hash Partitioning

```sql
CREATE TABLE events (
    event_id BIGINT,
    event_type VARCHAR(50),
    created_at TIMESTAMPTZ
) PARTITION BY HASH (event_id);

CREATE TABLE events_p0 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE events_p1 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE events_p2 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE events_p3 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

---

## Parallel Query

```sql
-- Check if parallel query is enabled
SHOW max_parallel_workers_per_gather;

-- Enable for a session
SET max_parallel_workers_per_gather = 4;

-- Force parallel (for testing)
SET min_parallel_table_scan_size = 0;
SET min_parallel_index_scan_size = 0;
SET parallel_tuple_cost = 0;
SET parallel_setup_cost = 0;

-- Check parallel workers in query plan
EXPLAIN (ANALYZE, VERBOSE) 
SELECT COUNT(*) FROM large_table;
-- Workers Planned: 4, Workers Launched: 4
```

---

## Summary

| Technique | Purpose |
|-----------|---------|
| **EXPLAIN ANALYZE** | Diagnose query performance |
| **Indexes** | Speed up reads |
| **VACUUM** | Reclaim dead tuple space |
| **ANALYZE** | Update query planner statistics |
| **Connection Pooling** | Handle many connections efficiently |
| **Partitioning** | Manage very large tables |
| **Parallel Query** | Use multiple CPU cores |
| **Configuration Tuning** | Optimize memory and I/O |

---
*Previous: [10 - Views & Materialized Views](10-views-materialized-views.md) | Next: [12 - Deep Concepts: ACID & MVCC](12-deep-concepts-acid-mvcc.md)*
