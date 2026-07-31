---
tags: [postgresql, admin, configuration, postgresql-conf]
---

# Configuration

Key settings in `postgresql.conf`. Use [PGTune](https://pgtune.leopard.in.ua) to generate a starting config.

## Memory (The Big Four)

```ini
shared_buffers = 4GB              # 25% of RAM
effective_cache_size = 12GB       # 75% of RAM (planner hint, not allocated)
work_mem = 64MB                   # per-sort/hash (multiplies per query!)
maintenance_work_mem = 1GB        # for VACUUM, CREATE INDEX
```

## WAL and Checkpoints

```ini
wal_buffers = 64MB
max_wal_size = 4GB
min_wal_size = 1GB
checkpoint_timeout = 15min
checkpoint_completion_target = 0.9
wal_compression = on
```

## Connections

```ini
max_connections = 200             # keep low; use PgBouncer for pooling
superuser_reserved_connections = 5
```

## Planner

```ini
random_page_cost = 1.1            # for SSDs (default 4.0 is for HDDs)
effective_io_concurrency = 200    # SSD-only; HDD use 1-2
default_statistics_target = 200
```

## Parallelism

```ini
max_worker_processes = 16
max_parallel_workers = 16
max_parallel_workers_per_gather = 4
```

## Logging

```ini
log_line_prefix = '%m [%p] %u@%d %h '
log_min_duration_statement = 1000  # log queries > 1s
log_checkpoints = on
log_connections = on
log_lock_waits = on
log_temp_files = 0
log_autovacuum_min_duration = 0
```

## Reload vs Restart

```sql
-- Reload config without restart (most settings)
SELECT pg_reload_conf();

-- Some settings require restart: shared_buffers, max_connections, wal_level
```

## Next

- [[05-Administration/05-Monitoring|Monitoring]]
- [[05-Administration/06-Security|Security]]
