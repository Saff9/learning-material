# 07 - Transactions & ACID

## Understanding Transactions

A **transaction** is a single unit of work that either completes entirely or fails entirely. It ensures database consistency.

```
┌──────────────────────────────────────────────────────────────┐
│                    TRANSACTION FLOW                           │
│                                                              │
│  BEGIN ──► Operation 1 ──► Operation 2 ──► Operation 3       │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ All succeed?                                        │    │
│  │  YES ──► COMMIT (permanent)                         │    │
│  │  NO  ──► ROLLBACK (undo everything)                 │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Transaction Commands

### BEGIN / START TRANSACTION

```sql
-- Start a transaction
BEGIN;
-- or
START TRANSACTION;

-- Insert data
INSERT INTO accounts (name, balance) VALUES ('Alice', 1000);
INSERT INTO accounts (name, balance) VALUES ('Bob', 500);

-- Commit (make permanent)
COMMIT;
```

### ROLLBACK

```sql
BEGIN;

-- Transfer money
UPDATE accounts SET balance = balance - 100 WHERE name = 'Alice';
UPDATE accounts SET balance = balance + 100 WHERE name = 'Bob';

-- Oops! Wrong amount
ROLLBACK;  -- Everything undone, database unchanged
```

### SAVEPOINT

```sql
BEGIN;

INSERT INTO orders (customer_id, total) VALUES (1, 100);
SAVEPOINT after_order_insert;

INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 101, 2);
-- Oops, wrong product!
ROLLBACK TO SAVEPOINT after_order_insert;  -- Undo only the item insert

-- Try again
INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 102, 2);
COMMIT;
```

### RELEASE SAVEPOINT

```sql
BEGIN;
SAVEPOINT sp1;
-- ... operations ...
RELEASE SAVEPOINT sp1;  -- Remove savepoint, can't rollback to it anymore
COMMIT;
```

### Transaction States

```sql
-- Check current transaction status
SELECT txid_current();  -- Current transaction ID

-- Check for active transactions
SELECT * FROM pg_stat_activity WHERE state = 'idle in transaction';
```

---

## Isolation Levels

Isolation levels control how transactions interact with each other. Higher isolation means less concurrency but more consistency.

### Read Phenomena

| Phenomenon | Description |
|------------|-------------|
| **Dirty Read** | Reading uncommitted data from another transaction |
| **Non-repeatable Read** | Same query returns different data within a transaction |
| **Phantom Read** | Same query returns different row count within a transaction |
| **Serialization Anomaly** | Result depends on transaction order |

### Isolation Levels in PostgreSQL

| Level | Dirty Read | Non-repeatable | Phantom | Serialization |
|-------|------------|----------------|---------|---------------|
| **READ UNCOMMITTED** | Not possible in PG | - | - | - |
| **READ COMMITTED** | No | Yes | Yes | Yes |
| **REPEATABLE READ** | No | No | Yes* | Yes |
| **SERIALIZABLE** | No | No | No | No |

*In PostgreSQL, REPEATABLE READ actually prevents phantom reads too!

### READ COMMITTED (Default)

```sql
-- Transaction A
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
-- Not committed yet!

-- Transaction B (concurrent)
BEGIN;
SELECT balance FROM accounts WHERE id = 1;
-- Sees OLD value (1000), not uncommitted change
-- No dirty read!

-- Transaction A
COMMIT;

-- Transaction B
SELECT balance FROM accounts WHERE id = 1;
-- Now sees NEW value (900) -- non-repeatable read!
COMMIT;
```

### REPEATABLE READ

```sql
-- Transaction A
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT balance FROM accounts WHERE id = 1;  -- 1000

-- Transaction B
BEGIN;
UPDATE accounts SET balance = 900 WHERE id = 1;
COMMIT;

-- Transaction A
SELECT balance FROM accounts WHERE id = 1;  -- Still 1000! (repeatable)
UPDATE accounts SET balance = balance - 50 WHERE id = 1;
-- ERROR: could not serialize access due to concurrent update
ROLLBACK;
```

### SERIALIZABLE

```sql
-- Transaction A
BEGIN ISOLATION LEVEL SERIALIZABLE;
SELECT SUM(balance) FROM accounts;  -- 1500

-- Transaction B
BEGIN ISOLATION LEVEL SERIALIZABLE;
INSERT INTO accounts (name, balance) VALUES ('Charlie', 500);
COMMIT;

-- Transaction A
SELECT SUM(balance) FROM accounts;  -- Still 1500! (no phantom read)
INSERT INTO accounts (name, balance) VALUES ('Diana', 300);
COMMIT;  -- May succeed or fail with serialization error
```

### Setting Isolation Level

```sql
-- Per transaction
BEGIN ISOLATION LEVEL SERIALIZABLE;

-- Or
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- Per session
SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Check current level
SHOW transaction_isolation;
```

---

## Locking

### Row-Level Locks

```sql
-- FOR UPDATE: Exclusive lock on selected rows
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
-- Other transactions cannot modify or lock this row until commit
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;

-- FOR SHARE: Shared lock (others can read, not update)
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR SHARE;
-- Others can SELECT but not UPDATE/DELETE this row
COMMIT;

-- FOR NO KEY UPDATE: Weaker than FOR UPDATE
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR NO KEY UPDATE;
-- Others can SELECT, UPDATE non-key columns, but not DELETE
COMMIT;

-- FOR KEY SHARE: Weakest lock
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR KEY SHARE;
-- Others can SELECT, UPDATE, DELETE, but not UPDATE key columns
COMMIT;
```

### Table-Level Locks

```sql
-- Explicit table locks
BEGIN;
LOCK TABLE accounts IN ACCESS EXCLUSIVE MODE;
-- Most restrictive, blocks all access

LOCK TABLE accounts IN SHARE MODE;
-- Others can read but not modify

LOCK TABLE accounts IN ROW EXCLUSIVE MODE;
-- Default for UPDATE/DELETE/INSERT
COMMIT;
```

### Lock Modes Compatibility

```
                    Requested Lock
                 ┌────┬────┬────┬────┬────┬────┬────┬────┐
                 │ACEX│ROWE│SHUP│SHAR│ROWU│EXCL│ACSH│ROWA│
    ┌────────────┼────┼────┼────┼────┼────┼────┼────┼────┤
    │ACCESS EXCL │ ✗  │ ✗  │ ✗  │ ✗  │ ✗  │ ✗  │ ✗  │ ✗  │
Held│ROW EXCL    │ ✗  │ ✗  │ ✗  │ ✗  │ ✗  │ ✗  │ ✗  │ ✓  │
    │SHARE UPDATE│ ✗  │ ✗  │ ✗  │ ✗  │ ✗  │ ✗  │ ✓  │ ✓  │
    │SHARE       │ ✗  │ ✗  │ ✗  │ ✓  │ ✗  │ ✓  │ ✓  │ ✓  │
    │ROW SHARE   │ ✗  │ ✗  │ ✓  │ ✓  │ ✓  │ ✓  │ ✓  │ ✓  │
    │EXCLUSIVE   │ ✗  │ ✗  │ ✗  │ ✓  │ ✗  │ ✓  │ ✓  │ ✗  │
    │ACCESS SHARE│ ✗  │ ✓  │ ✓  │ ✓  │ ✓  │ ✓  │ ✓  │ ✓  │
    │ROW ACCESS  │ ✗  │ ✓  │ ✓  │ ✓  │ ✓  │ ✓  │ ✓  │ ✓  │
    └────────────┴────┴────┴────┴────┴────┴────┴────┴────┘
    ✓ = Compatible  ✗ = Conflicting
```

### Advisory Locks

Application-level locks that don't conflict with table locks.

```sql
-- Session-level advisory lock
SELECT pg_advisory_lock(42);  -- Lock key 42
-- ... do work ...
SELECT pg_advisory_unlock(42);

-- Transaction-level (auto-released on commit/rollback)
SELECT pg_advisory_xact_lock(42);

-- Try to acquire (non-blocking)
SELECT pg_try_advisory_lock(42);  -- Returns true/false

-- Multiple keys
SELECT pg_advisory_lock(1, 2);  -- Two-key lock

-- Check locks
SELECT * FROM pg_locks WHERE locktype = 'advisory';
```

### Deadlocks

```sql
-- Transaction A
BEGIN;
UPDATE accounts SET balance = 900 WHERE id = 1;  -- Locks row 1
-- ... some work ...
UPDATE accounts SET balance = 400 WHERE id = 2;  -- Tries to lock row 2

-- Transaction B (concurrent)
BEGIN;
UPDATE accounts SET balance = 400 WHERE id = 2;  -- Locks row 2
-- ... some work ...
UPDATE accounts SET balance = 900 WHERE id = 1;  -- Tries to lock row 1
-- DEADLOCK! PostgreSQL detects and aborts one transaction
```

**Preventing Deadlocks:**
1. Always lock resources in the same order
2. Keep transactions short
3. Use lower isolation levels when possible
4. Use `NOWAIT` or `SKIP LOCKED`

```sql
-- NOWAIT: Fail immediately if locked
SELECT * FROM accounts WHERE id = 1 FOR UPDATE NOWAIT;

-- SKIP LOCKED: Skip locked rows
SELECT * FROM accounts WHERE status = 'pending' FOR UPDATE SKIP LOCKED;
-- Useful for queue processing with multiple workers
```

---

## MVCC (Multi-Version Concurrency Control)

PostgreSQL uses MVCC instead of read locks. Each transaction sees a snapshot of data.

```
Timeline:
T1 ──► BEGIN ──► SELECT (sees v1) ──► SELECT (still v1) ──► COMMIT
T2 ─────────────► UPDATE (creates v2) ──► COMMIT
T3 ────────────────────────► BEGIN ──► SELECT (sees v2) ──► COMMIT

Data Versions:
┌─────────────────────────────────────────┐
│ Row: id=1, name='Alice'                 │
│                                         │
│ Version 1: name='Alice', xmin=100       │  ← T1 sees this
│ Version 2: name='Alicia', xmin=200      │  ← T2 created, T3 sees this
│                                         │
│ T1 (txid=100) started before T2 (txid=200)│
│ So T1 sees v1, T3 (txid=300) sees v2    │
└─────────────────────────────────────────┘
```

### Visibility Rules

```sql
-- Check row versions
SELECT 
    xmin,           -- Transaction that created this row
    xmax,           -- Transaction that deleted/updated this row (0 = active)
    ctid,           -- Physical location (block, offset)
    *
FROM employees
WHERE id = 1;

-- Check dead tuples (waiting for vacuum)
SELECT 
    relname,
    n_live_tup,
    n_dead_tup,
    n_dead_tup::FLOAT / NULLIF(n_live_tup, 0) AS dead_ratio
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000;
```

### Vacuum and Autovacuum

```sql
-- Manual vacuum (reclaim space, update statistics)
VACUUM employees;

-- Vacuum with analyze
VACUUM ANALYZE employees;

-- Full vacuum (more aggressive, locks table)
VACUUM FULL employees;

-- Check vacuum stats
SELECT 
    schemaname, 
    relname,
    last_vacuum,
    last_autovacuum,
    vacuum_count,
    autovacuum_count
FROM pg_stat_user_tables;
```

---

## Practical Transaction Patterns

### Banking Transfer

```sql
BEGIN;

-- Check sender has enough funds
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;
-- If balance >= amount, proceed:

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

-- Insert transaction log
INSERT INTO transactions (from_account, to_account, amount, status)
VALUES (1, 2, 100, 'completed');

COMMIT;
```

### Queue Processing

```sql
-- Worker 1
BEGIN;
SELECT * FROM jobs 
WHERE status = 'pending' 
ORDER BY created_at 
FOR UPDATE SKIP LOCKED 
LIMIT 1;
-- Gets job 1, locks it

UPDATE jobs SET status = 'processing', worker_id = 1 WHERE id = ?;
COMMIT;

-- Worker 2 (concurrent)
BEGIN;
SELECT * FROM jobs 
WHERE status = 'pending' 
ORDER BY created_at 
FOR UPDATE SKIP LOCKED 
LIMIT 1;
-- Gets job 2 (skips locked job 1)

UPDATE jobs SET status = 'processing', worker_id = 2 WHERE id = ?;
COMMIT;
```

### Optimistic Locking

```sql
-- Add version column
ALTER TABLE products ADD COLUMN version INTEGER DEFAULT 1;

-- Read
SELECT id, name, price, version FROM products WHERE id = 1;
-- version = 5

-- Later, update with version check
UPDATE products 
SET price = 29.99, version = version + 1 
WHERE id = 1 AND version = 5;

-- If 0 rows affected, someone else updated it. Retry.
```

---

## Summary

| Command | Purpose |
|---------|---------|
| `BEGIN` | Start transaction |
| `COMMIT` | Save changes |
| `ROLLBACK` | Discard changes |
| `SAVEPOINT` | Create rollback point |
| `ROLLBACK TO` | Rollback to savepoint |
| `SET TRANSACTION` | Set isolation level |
| `FOR UPDATE` | Lock rows for update |
| `FOR SHARE` | Shared lock on rows |
| `SKIP LOCKED` | Skip locked rows |
| `NOWAIT` | Fail if locked |

| Isolation Level | Dirty Read | Non-repeatable | Phantom |
|-----------------|------------|----------------|---------|
| READ COMMITTED | No | Yes | Yes |
| REPEATABLE READ | No | No | No* |
| SERIALIZABLE | No | No | No |

---
*Previous: [06 - Advanced SQL](06-advanced-sql.md) | Next: [08 - Functions & Triggers](08-functions-triggers.md)*
