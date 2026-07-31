---
tags: [postgresql, extensions, pg_stat_statements, performance]
---

# pg_stat_statements — Query Performance

The single most important extension for production PostgreSQL. Tracks stats per query.

## Setup

```ini
# postgresql.conf
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.max = 10000
pg_stat_statements.track = all
track_io_timing = on
```

```sql
-- Create the extension (after restart)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

## Top Slow Queries

```sql
SELECT
    substring(query, 1, 100) AS query,
    calls,
    round(total_exec_time::numeric, 2) AS total_ms,
    round(mean_exec_time::numeric, 2) AS avg_ms,
    rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

## Queries by Average Time

```sql
SELECT
    substring(query, 1, 100) AS query,
    calls,
    round(mean_exec_time::numeric, 2) AS avg_ms
FROM pg_stat_statements
WHERE calls > 10  -- filter out one-offs
ORDER BY mean_exec_time DESC
LIMIT 10;
```

## Reset Stats

```sql
-- Reset after a tuning change
SELECT pg_stat_statements_reset();
```

## Next

- [[06-Extensions/03-pg_trgm|pg_trgm]]
- [[05-Administration/05-Monitoring|Monitoring]]
