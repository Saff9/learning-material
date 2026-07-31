# 08 - Transactions, Concurrency & MVCC

> ACID, isolation levels, locking, deadlocks, MVCC internals, vacuum, PgBouncer connection pooling, replication, distributed transactions, and advanced bloat management.

---

## Transaction Basics & Distributed Transactions

At the core of PostgreSQL's reliability is its implementation of ACID properties (Atomicity, Consistency, Isolation, Durability) for every transaction.

```sql
BEGIN;
-- or START TRANSACTION;

INSERT INTO accounts (name, balance) VALUES ('Alice', 1000);
INSERT INTO accounts (name, balance) VALUES ('Bob', 500);

COMMIT;
-- or ROLLBACK;
```

### SAVEPOINTs (Subtransactions)

Savepoints allow you to roll back parts of a transaction without aborting the entire transaction. Under the hood, PostgreSQL implements these as subtransactions.

> [!WARNING]
> Heavy use of subtransactions (and exceptions in PL/pgSQL which create implicit subtransactions) can cause severe performance degradation due to subtransaction cache overflows (SubtransSLRU). Use them sparingly in high-throughput systems.

```sql
BEGIN;
INSERT INTO orders (customer_id, total) VALUES (1, 100);
SAVEPOINT after_order;

INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 101, 2);
-- Oops, wrong product!
ROLLBACK TO SAVEPOINT after_order;

INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 102, 2);
COMMIT;
```

### Two-Phase Commit (2PC) & Distributed Transactions

For distributed systems requiring transactions across multiple databases, PostgreSQL supports Two-Phase Commit.

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
-- Phase 1: Prepare (persists state to disk, holds locks)
PREPARE TRANSACTION 'tx_transfer_123';

-- Phase 2: Commit (can be issued from a different connection)
COMMIT PREPARED 'tx_transfer_123';
-- Or ROLLBACK PREPARED 'tx_transfer_123';
```

---

## Connection Pooling & PgBouncer

Because PostgreSQL forks a new process for each connection (which is memory-heavy), connection poolers are essential for high-concurrency environments. **PgBouncer** is the standard.

PgBouncer supports three pooling modes:
1. **Session Pooling**: A client gets a connection for its entire lifespan.
2. **Transaction Pooling**: A client gets a connection only for the duration of a single transaction. (Most common and scalable).
3. **Statement Pooling**: Connections are returned to the pool after every statement. (Breaks multi-statement transactions).

> [!IMPORTANT]
> If using **Transaction Pooling** with PgBouncer, you cannot use session-level features like `PREPARE` statements (unless `max_prepared_statements` is managed correctly via PgBouncer), session-level advisory locks, or `SET local_work_mem = ...` safely across transactions.

---

## Isolation Levels

PostgreSQL provides robust isolation without read locks (thanks to MVCC).

| Level | Dirty Read | Non-repeatable | Phantom | Serialization |
|-------|------------|----------------|---------|---------------|
| READ COMMITTED | No | Yes | Yes | Yes |
| REPEATABLE READ | No | No | No* | Yes |
| SERIALIZABLE | No | No | No | No |

*PostgreSQL's REPEATABLE READ prevents phantom reads inherently due to snapshot isolation!

```sql
-- Default: READ COMMITTED
BEGIN;
SELECT balance FROM accounts WHERE id = 1;  -- 1000
-- Another transaction commits update to 900
SELECT balance FROM accounts WHERE id = 1;  -- 900 (non-repeatable)
COMMIT;

-- REPEATABLE READ
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT balance FROM accounts WHERE id = 1;  -- 1000
-- Another transaction commits update
SELECT balance FROM accounts WHERE id = 1;  -- Still 1000!
UPDATE accounts SET balance = balance - 50 WHERE id = 1;
-- Error: could not serialize access due to concurrent update
COMMIT;

-- SERIALIZABLE (SSI - Serializable Snapshot Isolation)
BEGIN ISOLATION LEVEL SERIALIZABLE;
-- Tracks read/write dependencies to prevent anomalies like Write Skew.
-- Applications must be prepared to retry on serialization_failure.
COMMIT;
```

---

## Locking & Concurrency

### Row-Level Locks

Row-level locks are actually stored in the row tuple header itself (`xmax` and infomask bits), which means acquiring a row lock requires writing to the disk (or memory buffers).

```sql
-- FOR UPDATE: Exclusive lock (prevents updates, deletes, and other FOR UPDATE/SHARE)
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;

-- FOR SHARE: Shared lock (prevents updates, allows other FOR SHARE)
SELECT * FROM accounts WHERE id = 1 FOR SHARE;

-- FOR NO KEY UPDATE: Allows FOR KEY SHARE (useful when updating non-unique/foreign key columns)
SELECT * FROM accounts WHERE id = 1 FOR NO KEY UPDATE;

-- FOR KEY SHARE: Weakest (protects foreign key references)
SELECT * FROM accounts WHERE id = 1 FOR KEY SHARE;
```

### Advisory Locks

Application-level locks managed by PostgreSQL. Excellent for leader election or preventing concurrent cron jobs.

```sql
-- Session-level (persists until disconnected or explicitly unlocked)
SELECT pg_advisory_lock(42);
SELECT pg_advisory_unlock(42);

-- Transaction-level (auto-released at COMMIT/ROLLBACK)
SELECT pg_advisory_xact_lock(42);

-- Try to acquire (non-blocking, returns boolean)
SELECT pg_try_advisory_lock(42);
```

### SKIP LOCKED (Queue Processing)

Perfect for implementing high-concurrency job queues directly in Postgres without external tools like Redis.

```sql
-- Worker 1
BEGIN;
SELECT * FROM jobs 
WHERE status = 'pending' 
ORDER BY created_at 
FOR UPDATE SKIP LOCKED 
LIMIT 1;
UPDATE jobs SET status = 'processing' WHERE id = ?;
COMMIT;
```

### Deadlocks

PostgreSQL detects deadlocks automatically. If two transactions wait on each other, one is aborted after `deadlock_timeout` (default 1s).
Diagnose blocking queries using the `pg_locks` and `pg_stat_activity` views.

---

## MVCC Deep Dive & Bloat

PostgreSQL uses Multi-Version Concurrency Control (MVCC). Instead of updating a row in-place, it creates a new version of the row and marks the old one as dead.

Every row (tuple) has system columns:
- `xmin`: Transaction ID (XID) that created it
- `xmax`: Transaction ID that deleted/updated it (0 = alive)
- `cmin`/`cmax`: Command identifiers within a transaction
- `ctid`: Physical location (block and offset) of the row

### HOT (Heap-Only Tuples) Updates

If an `UPDATE` does not modify any indexed columns, and there is free space in the same page block, PostgreSQL performs a HOT update.
- HOT updates avoid creating new index entries.
- They drastically reduce index bloat and vacuum overhead.
- **Tuning tip**: Use `FILLFACTOR = 90` on heavily updated tables to leave room in pages for HOT updates.

```sql
-- See row versions and CTIDs
SELECT xmin, xmax, ctid, * FROM employees WHERE id = 1;

-- Check dead tuples (bloat indicator)
SELECT relname, n_live_tup, n_dead_tup,
    ROUND(n_dead_tup::NUMERIC / NULLIF(n_live_tup, 0) * 100, 2) AS dead_ratio
FROM pg_stat_user_tables 
ORDER BY n_dead_tup DESC;
```

### Transaction ID (XID) Wraparound

Transaction IDs are 32-bit (about 4 billion). To prevent running out, old rows are "frozen" via VACUUM, marking their `xmin` as a special `FrozenTransactionId` (which is older than all normal XIDs). If autovacuum cannot keep up, the database will shut down to prevent data corruption.

---

## VACUUM & Online Maintenance

Dead tuples aren't physically removed immediately; `VACUUM` marks their space as reusable.

```sql
-- Standard (reclaims space for future inserts, does NOT shrink file, non-blocking)
VACUUM employees;

-- With analyze (updates planner statistics)
VACUUM ANALYZE employees;

-- Full (shrinks file, rewrites table, takes ACCESS EXCLUSIVE lock!)
-- AVOID IN PRODUCTION ON LARGE TABLES
VACUUM FULL employees;
```

### Online Bloat Removal (pg_repack / pg_squeeze)

Since `VACUUM FULL` blocks all access, modern production systems use extensions like `pg_repack` or `pg_squeeze` to rebuild tables online with minimal locking. They work by creating a new table, copying data, tracking changes via triggers, and swapping the tables.

### Autovacuum Tuning

Default autovacuum settings are often too passive for large databases.

```conf
autovacuum = on
autovacuum_max_workers = 3
-- Lower scale factors so vacuum triggers more often on large tables
autovacuum_vacuum_scale_factor = 0.05  -- Default 0.2 (20% is too high for a 100GB table)
autovacuum_analyze_scale_factor = 0.05
-- Reduce cost delay to let vacuum work faster
autovacuum_vacuum_cost_delay = 2ms     -- Default 20ms in older PG versions
```

---

## Replication & Concurrency

When running Read Replicas (Hot Standby), long-running queries on the replica can conflict with WAL replay (e.g., if the primary vacuums a row the replica is currently reading).

Settings to manage this:
- `max_standby_streaming_delay`: How long the replica will pause WAL replay to allow a query to finish before canceling the query.
- `hot_standby_feedback = on`: The replica tells the primary about its oldest active transaction, preventing the primary from vacuuming those rows. (Warning: This can cause bloat on the primary if a replica query hangs).

---

## Security: Row-Level Security (RLS)

RLS restricts which rows a user can read or modify, functioning like an automatic `WHERE` clause.

```sql
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;

CREATE POLICY employee_self_access ON employees
    FOR ALL
    USING (current_user = username);
    
-- A user querying SELECT * FROM employees will now only see their own row.
```

---
*Previous: 07 - Advanced SQL | Next: 09 - Functions & Procedures*
