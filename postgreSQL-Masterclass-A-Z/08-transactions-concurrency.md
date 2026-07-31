# 08 - Transactions, Concurrency & MVCC

> ACID, isolation levels, locking, deadlocks, MVCC internals, and vacuum.

---

## Transaction Basics

```sql
BEGIN;
-- or START TRANSACTION;

INSERT INTO accounts (name, balance) VALUES ('Alice', 1000);
INSERT INTO accounts (name, balance) VALUES ('Bob', 500);

COMMIT;
-- or ROLLBACK;
```

### SAVEPOINTs

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

---

## Isolation Levels

| Level | Dirty Read | Non-repeatable | Phantom | Serialization |
|-------|------------|----------------|---------|---------------|
| READ COMMITTED | No | Yes | Yes | Yes |
| REPEATABLE READ | No | No | No* | Yes |
| SERIALIZABLE | No | No | No | No |

*PostgreSQL's REPEATABLE READ prevents phantom reads too!

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
-- May error: could not serialize access due to concurrent update
COMMIT;

-- SERIALIZABLE
BEGIN ISOLATION LEVEL SERIALIZABLE;
-- Strongest guarantee, may fail with serialization_error
COMMIT;
```

---

## Locking

### Row-Level Locks

```sql
-- FOR UPDATE: Exclusive lock
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;

-- FOR SHARE: Shared lock
SELECT * FROM accounts WHERE id = 1 FOR SHARE;

-- FOR NO KEY UPDATE: Weaker than FOR UPDATE
SELECT * FROM accounts WHERE id = 1 FOR NO KEY UPDATE;

-- FOR KEY SHARE: Weakest
SELECT * FROM accounts WHERE id = 1 FOR KEY SHARE;
```

### Advisory Locks

```sql
-- Session-level
SELECT pg_advisory_lock(42);
-- ... do work ...
SELECT pg_advisory_unlock(42);

-- Transaction-level (auto-released)
SELECT pg_advisory_xact_lock(42);

-- Try to acquire (non-blocking)
SELECT pg_try_advisory_lock(42);
```

### SKIP LOCKED (Queue Processing)

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

-- Worker 2 (concurrent)
-- Gets next available job, skips locked one
```

---

## MVCC Deep Dive

PostgreSQL uses MVCC instead of read locks. Every row has:
- `xmin`: Transaction that created it
- `xmax`: Transaction that deleted it (0 = alive)

```sql
-- See row versions
SELECT xmin, xmax, ctid, * FROM employees WHERE id = 1;

-- Check dead tuples
SELECT relname, n_live_tup, n_dead_tup,
    ROUND(n_dead_tup::NUMERIC / NULLIF(n_live_tup, 0) * 100, 2) AS dead_ratio
FROM pg_stat_user_tables WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

---

## VACUUM

```sql
-- Standard (reclaims space, no file shrink)
VACUUM employees;

-- With analyze
VACUUM ANALYZE employees;

-- Full (shrinks file, locks table)
VACUUM FULL employees;

-- Verbose
VACUUM (VERBOSE, ANALYZE) employees;
```

### Autovacuum Tuning

```conf
autovacuum = on
autovacuum_max_workers = 3
autovacuum_vacuum_scale_factor = 0.05
autovacuum_analyze_scale_factor = 0.05
autovacuum_vacuum_cost_delay = 2ms
```

---
*Previous: 07 - Advanced SQL | Next: 09 - Functions & Procedures*
