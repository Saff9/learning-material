# 19 - Monitoring & Observability

> Built-in statistics, pg_stat_statements, slow query logging, alerting, and external monitoring tools.

---

## Built-in Statistics Views

PostgreSQL provides a robust set of dynamic statistics views that track activity and performance.

```sql
-- 1. Database Activity & Connections
-- Useful for finding long-running queries or "idle in transaction" sessions
SELECT pid, usename, client_addr, state, backend_start, xact_start, query_start, 
       EXTRACT(EPOCH FROM now() - query_start) AS query_duration_sec, query
FROM pg_stat_activity
WHERE state != 'idle' 
ORDER BY query_duration_sec DESC;

-- 2. Table Statistics (Tuples and Vacuuming)
-- Tracks dead tuples which cause table bloat and indicate if autovacuum is keeping up
SELECT schemaname, relname, n_live_tup, n_dead_tup, 
       ROUND((n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0)) * 100, 2) AS dead_tup_pct,
       last_vacuum, last_autovacuum, last_analyze
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;

-- 3. Index Usage
-- Identifies unused indexes which slow down writes, or highly used indexes
SELECT schemaname, relname, indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes 
ORDER BY idx_scan ASC; -- Find unused indexes

-- 4. Database-level Stats
-- Provides high-level metrics on commits, rollbacks, and cache hits
SELECT datname, numbackends, xact_commit, xact_rollback, 
       blks_read, blks_hit, tup_returned, tup_fetched
FROM pg_stat_database;

-- 5. I/O Statistics (PostgreSQL 16+)
-- Deeper insight into storage subsystem performance
SELECT * FROM pg_stat_io;

-- 6. WAL Statistics
-- Monitor write-ahead log generation rates
SELECT * FROM pg_stat_wal;

-- 7. Replication Lag
-- Monitor physical streaming replication delay
SELECT client_addr, application_name, state, sync_state,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) AS replication_lag_bytes,
       EXTRACT(EPOCH FROM write_lag) AS write_lag_sec,
       EXTRACT(EPOCH FROM replay_lag) AS replay_lag_sec
FROM pg_stat_replication;
```

---

## pg_stat_statements (Advanced Query Profiling)

`pg_stat_statements` is the gold standard for tracking execution statistics of all SQL statements executed by a server. It requires modification to `postgresql.conf` (`shared_preload_libraries = 'pg_stat_statements'`).

```sql
-- Enable the extension in your database
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Top 10 queries consuming the most total time
SELECT query, calls, total_exec_time, mean_exec_time, rows,
       shared_blks_hit, shared_blks_read, shared_blks_written
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- Queries with the highest execution time per call (slowest queries)
SELECT query, calls, mean_exec_time, max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- I/O intensive queries (causing the most disk reads)
SELECT query, calls, shared_blks_read, shared_blks_hit,
       ROUND((shared_blks_hit::numeric / NULLIF(shared_blks_hit + shared_blks_read, 0)) * 100, 2) AS cache_hit_pct
FROM pg_stat_statements
ORDER BY shared_blks_read DESC
LIMIT 10;

-- Reset statistics (useful after deploying a fix or during a new profiling session)
SELECT pg_stat_statements_reset();
```

---

## Slow Query Logging and Analysis

PostgreSQL can log long-running queries, which can then be analyzed by tools like **pgBadger**.

```conf
# postgresql.conf settings
log_min_duration_statement = 1000    # Log any query taking > 1000ms (1 second)
log_min_duration_sample = 100        # Track queries > 100ms...
log_statement_sample_rate = 0.1      # ...but only log 10% of them to save disk I/O

# Best practices for log format (crucial for pgBadger)
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0
log_autovacuum_min_duration = 0
```

> **Pro Tip:** Use **pgBadger**, an external open-source tool, to parse these log files and generate rich HTML reports showing query latencies, connection trends, and locking issues.

---

## auto_explain

The `auto_explain` module provides a way to log execution plans of slow statements automatically, without having to run `EXPLAIN` manually.

```conf
# postgresql.conf
shared_preload_libraries = 'pg_stat_statements, auto_explain'
auto_explain.log_min_duration = '1s'
auto_explain.log_analyze = true      # Includes actual execution times (WARNING: can add overhead)
auto_explain.log_buffers = true      # Logs buffer usage (cache hits/misses)
auto_explain.log_timing = true
auto_explain.log_triggers = true
auto_explain.log_verbose = true
auto_explain.log_format = json       # JSON format is easier to parse programmatically
```

---

## Active Monitoring and Observability Stacks

Modern deployments rarely rely solely on SQL scripts. They integrate with observability stacks:

1. **Prometheus + Grafana:** 
   - Use `postgres_exporter` to scrape PostgreSQL metrics.
   - Dashboards in Grafana provide real-time visualization of cache hits, active connections, and replication lag.
2. **Datadog / New Relic:**
   - Agent-based monitoring that tracks query performance and infrastructure health.
3. **pgCenter / pg_activity:**
   - Terminal-based `top`-like tools for real-time Postgres monitoring.

---

## Key Metrics to Alert On

Define alerts to catch issues before they cause downtime.

| Metric | Warning Threshold | Critical Threshold | Action/Meaning |
|--------|---------|----------|----------------|
| **Replication lag** | > 1 GB or > 30s | > 10 GB or > 2m | Replicas falling behind; check network/disk I/O |
| **Connection usage** | > 80% | > 95% | Approaching `max_connections`; connection pooling needed |
| **Dead tuple ratio** | > 10% | > 25% | Autovacuum is failing to keep up; table bloat imminent |
| **Cache hit ratio** | < 95% | < 90% | Memory starvation; tune `shared_buffers` or add RAM |
| **Lock waits** | > 10/sec | > 50/sec | Transaction contention; check for unindexed foreign keys or long transactions |
| **Checkpoint frequency** | < 5 min | < 2 min | Excessive I/O; increase `max_wal_size` |
| **Transaction rollback rate** | > 1% | > 5% | Application errors or deadlock issues |

---

## Tracking Cache Hit Ratio (The Golden Metric)

A healthy database serves most of its data from RAM, not disk.

```sql
-- Calculate overall database cache hit ratio
SELECT 
    datname,
    blks_hit,
    blks_read,
    ROUND(blks_hit::NUMERIC / NULLIF(blks_hit + blks_read, 0) * 100, 2) AS cache_hit_ratio
FROM pg_stat_database
WHERE datname NOT IN ('template0', 'template1')
  AND (blks_hit + blks_read) > 0;
```
*Aim for > 99% for most OLTP workloads.*

---
*Previous: 18 - Replication | Next: 20 - Performance Tuning*
