# 17 - Backup & Recovery

> Logical backups, physical backups, PITR, and disaster recovery strategies.

---

## Logical Backups (pg_dump)

```bash
# Full database dump
pg_dump -U postgres -d appdb > appdb_backup.sql

# Custom format (compressed, selective restore)
pg_dump -U postgres -d appdb -Fc > appdb_backup.dump

# Plain SQL with inserts
pg_dump -U postgres -d appdb --inserts > appdb_inserts.sql

# Specific tables
pg_dump -U postgres -d appdb -t employees -t departments > tables.sql

# Exclude tables
pg_dump -U postgres -d appdb -T temp_* > appdb_no_temp.sql

# Data only
pg_dump -U postgres -d appdb --data-only > appdb_data.sql

# Schema only
pg_dump -U postgres -d appdb --schema-only > appdb_schema.sql

# Parallel dump (fast for large databases)
pg_dump -U postgres -d appdb -Fd -j 4 -f appdb_parallel/

# Entire cluster
pg_dumpall -U postgres > cluster_backup.sql
```

---

## Restore (pg_restore)

```bash
# Restore custom format
pg_restore -U postgres -d appdb appdb_backup.dump

# Restore single table
pg_restore -U postgres -d appdb -t employees appdb_backup.dump

# List contents
pg_restore -l appdb_backup.dump

# Restore with specific TOC entries
pg_restore -L toc.txt appdb_backup.dump

# Create database then restore
pg_restore -U postgres -C -d postgres appdb_backup.dump

# Parallel restore
pg_restore -U postgres -d appdb -j 4 appdb_parallel/
```

---

## Physical Backups (pg_basebackup)

```bash
# Base backup
pg_basebackup -h localhost -U replicator -D /backup/2026-07-15 -Fp -Xs -P

# With WAL streaming
pg_basebackup -h localhost -U replicator -D /backup/latest -Ft -z -P -X stream

# Incremental backup (PostgreSQL 17+)
pg_basebackup -h localhost -U replicator -D /backup/incr -Fp --incremental=/backup/full
```

---

## Point-in-Time Recovery (PITR)

### WAL Archiving Setup

```conf
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /archive/%f'
# Or use wal-g, pgBackRest, etc.

# Recovery target
recovery_target_time = '2026-07-15 14:30:00'
```

### Recovery Process

```bash
# 1. Stop PostgreSQL
sudo systemctl stop postgresql

# 2. Restore base backup
rm -rf /var/lib/postgresql/18/main/*
cp -r /backup/base/* /var/lib/postgresql/18/main/

# 3. Create recovery signal
touch /var/lib/postgresql/18/main/recovery.signal

# 4. Configure recovery
cat > /var/lib/postgresql/18/main/postgresql.auto.conf <<EOF
restore_command = 'cp /archive/%f %p'
recovery_target_time = '2026-07-15 14:30:00'
recovery_target_action = 'promote'
EOF

# 5. Start PostgreSQL
sudo systemctl start postgresql
```

---

## pgBackRest (Recommended)

```bash
# Install
sudo apt install pgbackrest

# Configure /etc/pgbackrest/pgbackrest.conf
[global]
repo1-path=/var/lib/pgbackrest
repo1-retention-full=2

[appdb]
pg1-path=/var/lib/postgresql/18/main

# Full backup
pgbackrest --stanza=appdb backup

# Incremental
pgbackrest --stanza=appdb backup --type=incr

# Restore
pgbackrest --stanza=appdb restore

# Check
pgbackrest --stanza=appdb info
```

---

## Backup Strategy

| Type | Tool | Frequency | Retention |
|------|------|-----------|-----------|
| Full logical | pg_dump | Weekly | 4 weeks |
| Full physical | pg_basebackup/pgBackRest | Daily | 7 days |
| Incremental | pgBackRest | Hourly | 24 hours |
| WAL archiving | archive_command | Continuous | 7 days |
| Cross-region | Cloud snapshots | Daily | 30 days |

---
*Previous: 16 - Security | Next: 18 - Replication & High Availability*
