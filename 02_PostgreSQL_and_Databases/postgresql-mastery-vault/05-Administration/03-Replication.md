---
tags: [postgresql, admin, replication, streaming, logical]
---

# Replication

## Physical (Streaming) Replication

Block-level WAL replication. Replica is read-only.

```ini
# Primary: postgresql.conf
wal_level = replica
max_wal_senders = 10
```

```sql
-- Create replication role
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'replpw';
```

```bash
# Standby: clone the primary
pg_basebackup -h primary -U replicator -D $PGDATA -Fp -Xs -P -R
pg_ctl start
```

## Logical Replication

Row-level replication. Can replicate to different versions, selective tables, writable target.

```sql
-- Publisher
CREATE PUBLICATION pub_sales FOR TABLE sales, customers;

-- Subscriber
CREATE SUBSCRIPTION sub_sales
    CONNECTION 'host=primary user=repl dbname=sales'
    PUBLICATION pub_sales;
```

## Synchronous vs Asynchronous

```ini
# Synchronous (no data loss, higher latency)
synchronous_standby_names = 'FIRST 2 (replica1, replica2)'

# Asynchronous (default — lower latency, may lose last few transactions on failover)
```

## When to Use Each

| | Physical | Logical |
|---|---|---|
| Cross-version | No | Yes |
| Selective tables | No | Yes |
| Writable target | No | Yes |
| DDL replicated | Yes | No |
| Setup complexity | Lower | Higher |

## Next

- [[05-Administration/04-Configuration|Configuration]]
- [[05-Administration/05-Monitoring|Monitoring]]
