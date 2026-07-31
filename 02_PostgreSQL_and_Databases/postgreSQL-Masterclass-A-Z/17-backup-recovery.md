# 17 - Backup & Recovery

> Comprehensive disaster recovery strategies, Logical Backups (`pg_dump`), Physical Backups (`pg_basebackup`), Point-in-Time Recovery (PITR), and Enterprise Backup solutions (`pgBackRest`).

---

## 1. Logical Backups (pg_dump & pg_restore)

Logical backups generate standard SQL scripts or custom archive files containing the commands to recreate the database. They do not lock the database (uses MVCC snapshots) and are highly portable across OS architectures and PostgreSQL versions.

### pg_dump
```bash
# Full database dump to plain SQL script
pg_dump -U postgres -d appdb > appdb_full.sql

# Custom format (-Fc) - Highly Recommended! 
# It compresses the output, is heavily optimized, and allows selective restores.
pg_dump -U postgres -d appdb -Fc > appdb_backup.dump

# Directory format (-Fd) with Parallelism (-j) 
# Best for large databases. Dumps multiple tables concurrently.
pg_dump -U postgres -d appdb -Fd -j 4 -f /backups/appdb_parallel/

# Specific Use Cases
pg_dump -U postgres -d appdb -t users -t orders > tables.sql     # Specific tables only
pg_dump -U postgres -d appdb --schema-only > schema.sql          # DDL only, no data
pg_dump -U postgres -d appdb --data-only > data.sql              # Data only, no DDL

# Backup entire cluster (all databases + global objects like Roles and Tablespaces)
pg_dumpall -U postgres > global_cluster_backup.sql
```

### pg_restore
```bash
# Restore a Custom Format dump (-Fc) to a database
pg_restore -U postgres -d appdb_dev appdb_backup.dump

# The Power of Custom Format: Selective Restore
# List Contents (TOC - Table of Contents)
pg_restore -l appdb_backup.dump > toc.txt
# Edit toc.txt (delete lines you don't want to restore)
# Restore using the modified TOC
pg_restore -L toc.txt -d appdb_dev appdb_backup.dump

# Restore with maximum parallelism (Fastest method)
# -C creates the DB, -e stops on error
pg_restore -U postgres -j 8 -C -e -d postgres appdb_backup.dump
```

**Pros of Logical Backups:** Easy to use, cross-version compatibility, selective restore.
**Cons:** Slow to backup/restore large DBs (>500GB), heavy CPU/Memory usage.

---

## 2. Physical Backups (pg_basebackup)

Physical backups make a binary copy of the actual database files on disk. They are much faster for massive databases and are required for setting up Replication and Point-in-Time Recovery.

```bash
# Take a base physical backup of the cluster
# -Xs streams the WAL logs generated during the backup so the backup is consistent
# -P shows progress, -Fp uses plain format (copies data directory structure)
pg_basebackup -h production-db -U replicator -D /backups/base_backup/ -Fp -Xs -P

# Compressed Tar format with streaming WAL
pg_basebackup -h production-db -U replicator -D /backups/archives/ -Ft -z -P -X stream

# Incremental physical backup (PostgreSQL 17+ Native feature)
# Massively saves disk space by only copying blocks that changed since the base backup.
pg_basebackup -h production-db -U replicator -D /backups/incr1/ -Fp \
    --incremental=/backups/base_backup/
```

---

## 3. Point-in-Time Recovery (PITR) & WAL Archiving

PITR is the ultimate disaster recovery feature. It allows you to restore the database to an exact second in the past (e.g., right before a developer accidentally ran `DROP TABLE users;`).

### Step 1: Configure Continuous Archiving on Primary
```conf
# postgresql.conf
wal_level = replica
archive_mode = on
# Copy WAL files to an archive directory (or use AWS S3 via tools like wal-e)
archive_command = 'test ! -f /mnt/nfs/archive/%f && cp %p /mnt/nfs/archive/%f'
```

### Step 2: The Disaster Happens (e.g., at 14:30:00)

### Step 3: Perform PITR Restoration
```bash
# 1. Stop PostgreSQL service
sudo systemctl stop postgresql

# 2. Safely move the current corrupted data directory (Don't delete it just in case!)
mv /var/lib/postgresql/18/main /var/lib/postgresql/18/main_corrupted

# 3. Restore the last known good Base Backup (taken via pg_basebackup)
cp -r /backups/base_backup /var/lib/postgresql/18/main
chown -R postgres:postgres /var/lib/postgresql/18/main

# 4. Create the recovery signal file
touch /var/lib/postgresql/18/main/recovery.signal

# 5. Tell PostgreSQL to restore up to the moment of disaster and stop
cat > /var/lib/postgresql/18/main/postgresql.auto.conf <<EOF
restore_command = 'cp /mnt/nfs/archive/%f %p'
recovery_target_time = '2026-07-15 14:29:59' # Right before the DROP TABLE
recovery_target_action = 'promote' # Open DB for writes after reaching target
EOF

# 6. Start PostgreSQL (It will replay all WAL logs up to the exact target time)
sudo systemctl start postgresql
```

---

## 4. Enterprise Backups: pgBackRest

Managing `pg_basebackup` and WAL archives manually is tedious and error-prone. **pgBackRest** is the industry standard for managing backups, offering parallel processing, compression, S3 integration, and delta restores.

### Architecture & Setup
```bash
sudo apt install pgbackrest

# Configure /etc/pgbackrest/pgbackrest.conf
[global]
repo1-path=/var/lib/pgbackrest
repo1-retention-full=2     # Keep 2 full backups
repo1-cipher-type=aes-256-cbc # Encrypt backups
repo1-cipher-pass=SuperSecretEncryptionKey

# Define a "Stanza" (a PostgreSQL cluster definition)
[appdb]
pg1-path=/var/lib/postgresql/18/main
```

### Operations
```bash
# Initialize the stanza
pgbackrest --stanza=appdb stanza-create

# 1. Full Backup (Weekly)
pgbackrest --stanza=appdb backup --type=full

# 2. Incremental Backup (Daily/Hourly) - Only backs up changed files since last backup
pgbackrest --stanza=appdb backup --type=incr

# 3. Restore a specific point in time
pgbackrest --stanza=appdb restore --type=time --target="2026-07-15 14:29:59"

# 4. Delta Restore (Blazing fast!)
# Instead of wiping the DB directory, it compares checksums and only restores what changed
pgbackrest --stanza=appdb restore --delta

# Info / Status check
pgbackrest info
```

---

## Enterprise Backup Strategy Recommendation

| Backup Type | Tool | Frequency | Retention | Purpose |
|-------------|------|-----------|-----------|---------|
| Continuous WAL | pgBackRest | Real-time | 14 days | Sub-second RPO, PITR capabilities |
| Incremental Physical | pgBackRest | Daily/Hourly | 14 days | Fast RTO (Recovery Time) |
| Full Physical | pgBackRest | Weekly | 4-8 weeks | Base for incrementals, DR |
| Full Logical | pg_dump -Fc | Monthly/Ad-hoc| 1 Year | Major version upgrades, archival |

---
*Previous: 16 - Security | Next: 18 - Replication & High Availability*
