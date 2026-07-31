---
tags: [postgresql, admin, backup, recovery, pitr]
---

# Backup and Recovery

## Logical Backups (pg_dump)

```bash
# Dump entire database (custom format — compressed, parallel-restore capable)
pg_dump -U postgres -Fc myapp -f myapp.dump

# Plain SQL script (portable across versions)
pg_dump -U postgres -Fp myapp > myapp.sql

# Dump specific tables only
pg_dump -U postgres --table=users --table=orders myapp > tables.sql

# Parallel dump (directory format, 4 jobs)
pg_dump -U postgres -Fd myapp -j 4 -f myapp_dir/

# All databases + roles + tablespaces
pg_dumpall -U postgres > cluster.sql
```

## Restore

```bash
# Restore from custom format
createdb myapp_new
pg_restore -U postgres -d myapp_new -j 4 myapp.dump

# Restore from SQL script
psql -U postgres -d myapp_new -f myapp.sql

# Restore specific table only
pg_restore -U postgres -d myapp -t users myapp.dump
```

## Physical Backups and PITR

```ini
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /var/wal_archive/%f && cp %p /var/wal_archive/%f'
```

```bash
# Take a base backup
pg_basebackup -h primary -U replicator -D /var/lib/postgresql/data -Fp -Xs -P -R
```

## Point-in-Time Recovery

```ini
# recovery settings (in postgresql.conf, PG12+)
restore_command = 'cp /var/wal_archive/%f %p'
recovery_target_time = '2026-07-15 14:30:00+00'
recovery_target_action = 'promote'
```

## Backup Strategy

> [!important] 3-2-1 Backup Rule
> - 3 copies of your data
> - 2 different storage types
> - 1 copy offsite
>
> For PostgreSQL: nightly pg_dump (logical) + continuous WAL archiving (physical PITR) + offsite copy.

## Next

- [[05-Administration/03-Replication|Replication]]
- [[05-Administration/04-Configuration|Configuration]]
