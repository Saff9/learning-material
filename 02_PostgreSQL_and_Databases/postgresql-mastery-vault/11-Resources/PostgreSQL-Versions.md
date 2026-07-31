---
tags: [resources, versions, reference]
---

# PostgreSQL Version History

## Current Versions (2026)

| Version | Status | Key Features |
|---------|--------|--------------|
| **18** (Sep 2025) | Stable (current) | Async I/O (io_uring), UUIDv7, virtual generated columns, OAuth 2.0, B-tree skip scans, RETURNING OLD/NEW |
| **17** (Sep 2024) | Supported (until Nov 2027) | JSON_TABLE, MERGE RETURNING, incremental backups, MAINTAIN privilege |
| **19 Beta 1** (Jun 2026) | Beta | REPACK CONCURRENTLY, parallel autovacuum, SQL/PGQ, GROUP BY ALL |

## Key Features by Version

### PostgreSQL 18 (Current Stable)
- **Async I/O**: 2-3x faster sequential scans with `io_uring` on Linux
- **UUIDv7**: Timestamp-ordered, sortable UUIDs (`uuidv7()`)
- **Virtual generated columns**: Computed at read-time (not stored)
- **OAuth 2.0**: Native JWT/OAuth authentication
- **B-tree skip scans**: Multicolumn indexes can skip leading columns
- **RETURNING OLD/NEW**: Get both old and new row values on UPDATE/DELETE
- **Failover slots**: Logical replication slots survive failover
- **Stats survive upgrades**: Planner stats preserved across `pg_upgrade`

### PostgreSQL 17
- **JSON_TABLE**: Turn JSON into relational rows
- **MERGE RETURNING**: Get affected rows from MERGE
- **Incremental backups**: `pg_basebackup` supports incremental
- **MAINTAIN privilege**: Grant VACUUM/ANALYZE without write access
- **Logical replication improvements**: Failover support, row filters

### PostgreSQL 16
- **Logical replication improvements**: Parallel apply, bi-directional
- **Query optimization**: Better statistics, improved parallelism
- **COPY improvements**: Faster bulk loading

### PostgreSQL 15
- **MERGE command**: Upsert on steroids
- **Logical replication**: Row filters and column lists
- **Sort performance**: Incremental sorting improvements

## Upgrade Path

```bash
# In-place upgrade (same major version)
sudo apt update && sudo apt upgrade postgresql-18

# Major version upgrade (17 → 18)
sudo pg_upgradecluster 17 main --method=upgrade

# Or use logical replication for zero-downtime
```

## Related

- [[Home]]
- [[11-Resources/|Resources]]
