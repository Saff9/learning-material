---
tags: [postgresql, admin, monitoring, pg_stat]
---

# Monitoring

## pg_stat_activity — Active Queries

```sql
-- See all active queries
SELECT pid, usename, datname, state, wait_event_type,
       NOW() - query_start AS runtime, query
FROM pg_stat_activity
WHERE state <> 'idle' AND pid <> pg_backend_pid();

-- Kill a long-running query
SELECT pg_terminate_backend(12345);  -- replace 12345 with the pid
```

## pg_stat_user_tables — Table Statistics

```sql
-- Tables with most dead tuples (need VACUUM)
SELECT relname, n_live_tup, n_dead_tup,
       last_vacuum, last_autovacuum, last_analyze
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

## pg_stat_user_indexes — Index Usage

```sql
-- Find unused indexes (idx_scan = 0)
SELECT schemaname, relname, indexrelname, idx_scan,
       pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

## Cache Hit Ratio

```sql
-- Should be > 99% for production
SELECT datname, blks_read, blks_hit,
       round(blks_hit::numeric / nullif(blks_hit + blks_read, 0) * 100, 2) AS hit_pct
FROM pg_stat_database
WHERE datname = current_database();
```

## Replication Lag

```sql
SELECT client_addr, state, sync_state,
       pg_wal_lsn_diff(pg_current_wal_lsn(), write_lsn) AS write_lag_bytes
FROM pg_stat_replication;
```

## Next

- [[05-Administration/06-Security|Security]]
- [[06-Extensions/02-pg_stat_statements|pg_stat_statements]]
