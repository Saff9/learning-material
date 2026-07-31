# 18 - Replication & High Availability

> Streaming replication, logical replication, failover, and HA architectures.

---

## Streaming Replication

### Primary Configuration

```conf
# postgresql.conf
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10
wal_keep_size = 1GB
hot_standby = on
archive_mode = on
archive_command = 'cp %p /archive/%f'
```

```sql
-- Create replication user
CREATE ROLE replicator WITH LOGIN REPLICATION PASSWORD 'ReplPass123!';
```

```conf
# pg_hba.conf
hostssl replication replicator 10.0.1.0/24 scram-sha-256
```

### Standby Setup

```bash
# 1. Stop standby
sudo systemctl stop postgresql

# 2. Clear data directory
rm -rf /var/lib/postgresql/18/main/*

# 3. pg_basebackup from primary
pg_basebackup -h primary-host -U replicator -D /var/lib/postgresql/18/main -Fp -Xs -P

# 4. Create standby signal
touch /var/lib/postgresql/18/main/standby.signal

# 5. Configure primary_conninfo
cat > /var/lib/postgresql/18/main/postgresql.auto.conf <<EOF
primary_conninfo = 'host=primary-host port=5432 user=replicator password=ReplPass123! sslmode=require'
EOF

# 6. Start standby
sudo systemctl start postgresql
```

---

## Synchronous Replication

```conf
# postgresql.conf (primary)
synchronous_commit = remote_apply
synchronous_standby_names = 'FIRST 1 (standby1, standby2)'
# or: ANY 1 (standby1, standby2)
```

---

## Logical Replication

```sql
-- On primary
CREATE PUBLICATION app_tables FOR TABLE users, orders, order_items;

-- On subscriber
CREATE SUBSCRIPTION app_sub
CONNECTION 'host=primary-host dbname=appdb user=replicator password=ReplPass123!'
PUBLICATION app_tables;

-- Check status
SELECT * FROM pg_stat_subscription;
```

---

## Failover Slots (PostgreSQL 17+)

```sql
-- Create failover slot (survives primary failover)
SELECT pg_create_physical_replication_slot('standby_slot', true, true);
```

---

## High Availability Tools

### Patroni (Recommended)

```yaml
# patroni.yml
scope: appdb
namespace: /db/
name: node1

restapi:
  listen: 0.0.0.0:8008
  connect_address: 10.0.1.10:8008

etcd:
  hosts: 10.0.1.1:2379,10.0.1.2:2379,10.0.1.3:2379

postgresql:
  listen: 0.0.0.0:5432
  connect_address: 10.0.1.10:5432
  data_dir: /var/lib/postgresql/18/main
  pgpass: /tmp/pgpass
  authentication:
    replication:
      username: replicator
      password: ReplPass123!
    superuser:
      username: postgres
      password: PostgresPass123!
```

### repmgr

```bash
# Register primary
repmgr -f /etc/repmgr.conf primary register

# Register standby
repmgr -f /etc/repmgr.conf standby register

# Manual failover
repmgr -f /etc/repmgr.conf standby promote
```

---

## Connection Pooling

### PgBouncer

```ini
[databases]
appdb = host=localhost port=5432 dbname=appdb

[pgbouncer]
listen_port = 6432
listen_addr = 127.0.0.1
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
```

| Pool Mode | Behavior | Use Case |
|-----------|----------|----------|
| Session | Connection lasts until disconnect | Long sessions, prepared statements |
| Transaction | Returned after each transaction | **Most applications (recommended)** |
| Statement | Returned after each statement | Read-only, no transactions |

---
*Previous: 17 - Backup | Next: 19 - Monitoring & Observability*
