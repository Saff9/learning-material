# 19 - Monitoring & Observability

> Built-in statistics, pg_stat_statements, slow query logging, and alerting.

---

## Built-in Statistics Views

```sql
-- Database activity
SELECT * FROM pg_stat_activity;

-- Table statistics
SELECT schemaname, relname, n_live_tup, n_dead_tup, 
       last_vacuum, last_autovacuum, last_analyze
FROM pg_stat_user_tables;

-- Index usage
SELECT schemaname, relname, indexrelname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes ORDER BY idx_scan DESC;

-- Database-level stats
SELECT datname, numbackends, xact_commit, xact_rollback, 
       blks_read, blks_hit, tup_returned, tup_fetched
FROM pg_stat_database;

-- I/O statistics (PostgreSQL 16+)
SELECT * FROM pg_stat_io;

-- WAL statistics
SELECT * FROM pg_stat_wal;

-- Replication lag
SELECT client_addr, state, sent_lsn, write_lsn, flush_lsn, replay_lsn,
       pg_size_pretty(pg_wal_lsn_diff(sent_lsn, replay_lsn)) AS lag
FROM pg_stat_replication;
```

---

## pg_stat_statements

```sql
-- Enable
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Top queries by total time
SELECT query, calls, total_exec_time, mean_exec_time, rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- Reset
SELECT pg_stat_statements_reset();
```

---

## Slow Query Logging

```conf
log_min_duration_statement = 1000    -- Log queries > 1 second
log_min_duration_sample = 100        -- Sample queries > 100ms
log_statement_sample_rate = 0.1      -- Log 10% of sampled queries
```

---

## auto_explain

```conf
shared_preload_libraries = 'auto_explain'
auto_explain.log_min_duration = '1s'
auto_explain.log_analyze = true
auto_explain.log_buffers = true
auto_explain.log_timing = true
auto_explain.log_triggers = true
auto_explain.log_verbose = true
auto_explain.log_format = text
```

---

## Key Metrics to Alert On

| Metric | Warning | Critical |
|--------|---------|----------|
| Replication lag | > 1 GB | > 10 GB |
| Connection usage | > 80% | > 95% |
| Dead tuple ratio | > 10% | > 25% |
| Cache hit ratio | < 95% | < 90% |
| Lock waits | > 10/s | > 50/s |
| Checkpoint frequency | < 5 min | < 2 min |
| Transaction rollback rate | > 1% | > 5% |

---

## Cache Hit Ratio

```sql
SELECT 
    datname,
    ROUND(blks_hit::NUMERIC / NULLIF(blks_hit + blks_read, 0) * 100, 2) AS cache_hit_ratio
FROM pg_stat_database
WHERE datname NOT IN ('template0', 'template1');
```

---
*Previous: 18 - Replication | Next: 20 - Performance Tuning*
