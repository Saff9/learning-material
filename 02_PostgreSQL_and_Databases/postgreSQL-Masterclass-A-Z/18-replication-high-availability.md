# 18 - Replication & High Availability

> Deep dive into Physical Streaming Replication, Logical Replication, Failover strategies, Patroni HA clusters, and Connection Pooling.

Replication in PostgreSQL ensures High Availability (HA), disaster recovery, and horizontal read scaling by maintaining live copies of your database on other servers.

---

## 1. Physical Streaming Replication

Physical replication copies the database byte-for-byte. The primary server streams its Write-Ahead Log (WAL) to standby servers, which constantly apply the WAL records. Standby servers are identical clones and are strictly read-only.

### Primary Server Configuration

```conf
# postgresql.conf on Primary
wal_level = replica               # Determines how much info is written to WAL
max_wal_senders = 10              # Max concurrent standby connections
max_replication_slots = 10        # Protects WAL files from deletion if a standby disconnects
hot_standby = on                  # Allow read-only queries on the standby
```

```sql
-- Create a dedicated role for replication
CREATE ROLE replicator WITH LOGIN REPLICATION PASSWORD 'ReplPass123!';
```

```conf
# pg_hba.conf on Primary
# Allow standby IPs to connect for replication
hostssl replication replicator 10.0.1.20/32 scram-sha-256
```

### Standby Server Setup

```bash
# 1. Stop standby service
sudo systemctl stop postgresql

# 2. Destroy the default data directory completely
rm -rf /var/lib/postgresql/18/main/*

# 3. Pull a base physical backup from the primary
# -R automatically creates the required postgresql.auto.conf and standby.signal!
pg_basebackup -h 10.0.1.10 -U replicator -D /var/lib/postgresql/18/main -Fp -Xs -P -R

# 4. Start standby (It automatically begins receiving and replaying WAL)
sudo systemctl start postgresql
```

### Monitoring Physical Replication
```sql
-- Run on Primary to see connected standbys and their replication lag
SELECT client_addr, state, sync_state, 
       pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes 
FROM pg_stat_replication;

-- Run on Standby to check recovery status
SELECT pg_is_in_recovery(); -- Returns TRUE
SELECT pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn();
```

---

## 2. Synchronous vs Asynchronous Replication

By default, streaming replication is **Asynchronous**. The primary commits a transaction locally and returns success to the client *before* the standby receives it. This is fast, but risks data loss if the primary explodes before the WAL is sent.

**Synchronous Replication** guarantees zero data loss (RPO = 0). The primary waits for the standby to acknowledge the write before telling the client "Success".

```conf
# postgresql.conf (Primary)

# Requires exactly one specific standby to acknowledge the commit
synchronous_standby_names = 'FIRST 1 (standby1, standby2)'

# Quorum based (Recommended for HA): Any 2 of the 3 standbys must acknowledge
synchronous_standby_names = 'ANY 2 (standby1, standby2, standby3)'

# Determines HOW FAR the commit must propagate before returning success
# options: on, remote_apply, remote_write, local
synchronous_commit = remote_apply 
```

---

## 3. Logical Replication (Pub/Sub)

Unlike Physical replication (byte-for-byte), Logical replication decodes WAL logs into SQL operations and applies them to the subscriber. 

**Advantages:**
- Can replicate specific tables (not just the whole cluster).
- Subscriber can be written to! (Multi-active potential, data aggregation).
- Can replicate across different PostgreSQL versions (great for zero-downtime upgrades).

**Limitations:**
- Cannot replicate DDL (CREATE TABLE, ALTER TABLE).
- Cannot replicate Sequences (you must sync them manually).

### Setup Logical Replication
```sql
-- On PRIMARY (Publisher)
wal_level = logical -- Required in postgresql.conf

CREATE PUBLICATION app_tables_pub FOR TABLE users, orders;
-- Or publish all tables: CREATE PUBLICATION all_tables_pub FOR ALL TABLES;

-- On STANDBY (Subscriber)
-- The tables MUST exist on the subscriber with the exact same schemas first!
CREATE SUBSCRIPTION app_sub
CONNECTION 'host=primary-db dbname=appdb user=replicator password=ReplPass!'
PUBLICATION app_tables_pub;

-- Monitor Logical Replication
SELECT * FROM pg_stat_subscription;
```

---

## 4. High Availability (HA) & Automatic Failover

If the Primary dies, a Standby must be promoted to Primary. Doing this manually is dangerous (Split-Brain scenarios). 

### Patroni (The Industry Standard for PostgreSQL HA)
Developed by Zalando, Patroni relies on a Distributed Consensus Store (Etcd, Consul, ZooKeeper) to manage failover logic seamlessly.

```yaml
# patroni.yml configuration overview
scope: my_pg_cluster
namespace: /db/
name: pg_node_1

# Etcd provides the distributed lock and consensus
etcd:
  hosts: 10.0.1.1:2379,10.0.1.2:2379,10.0.1.3:2379

postgresql:
  listen: 0.0.0.0:5432
  data_dir: /var/lib/postgresql/18/main
  # Patroni injects tags into postgresql.conf automatically
  parameters:
    max_connections: 500
    wal_level: replica
```
*When the primary goes down, Patroni nodes use Etcd to elect a new leader and automatically reconfigure the remaining standbys to follow the new leader.*

---

## 5. Connection Pooling

PostgreSQL connections are heavy OS processes. A database can usually only handle 500-1000 direct connections before crashing. Connection poolers sit in front of PG, handling thousands of client connections and multiplexing them over a small number of real database connections.

### PgBouncer Configuration

```ini
[databases]
# Alias = Real Database
appdb = host=127.0.0.1 port=5432 dbname=appdb

[pgbouncer]
listen_port = 6432
listen_addr = 0.0.0.0
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt

# Transaction pooling is critical for modern web apps!
pool_mode = transaction
max_client_conn = 10000     # Apps can open 10k connections
default_pool_size = 50      # PgBouncer only opens 50 real connections to PG
```

| Pool Mode | Behavior | Use Case |
|-----------|----------|----------|
| **Session** | Connection belongs to client until they disconnect | Legacy apps, heavy prepared statements |
| **Transaction**| Connection returned to pool after `COMMIT`/`ROLLBACK` | **95% of modern Web Apps / Microservices** |
| **Statement** | Connection returned after every single SQL query | Read-only analytic workloads (Rare) |

---
*Previous: 17 - Backup & Recovery | Next: 19 - Monitoring & Observability*
