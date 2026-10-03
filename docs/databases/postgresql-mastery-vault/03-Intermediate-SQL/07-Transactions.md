---
tags: [sql, intermediate, transactions, acid, isolation]
---

# Transactions

Transactions ensure data integrity by grouping operations into all-or-nothing units.

## ACID Properties

| Property | Meaning |
|----------|---------|
| **Atomicity** | All operations succeed or all fail (no partial) |
| **Consistency** | Data stays in a valid state (constraints enforced) |
| **Isolation** | Concurrent transactions don't interfere |
| **Durability** | Committed data survives crashes (WAL) |

## Basic Transactions

```sql
-- Transfer money between accounts
BEGIN;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
-- If any statement fails, use ROLLBACK instead of COMMIT

-- Or with explicit error handling
BEGIN;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    -- Oops, something went wrong
    ROLLBACK;
-- Both updates are undone
```

## SAVEPOINTs

```sql
BEGIN;
    INSERT INTO orders (customer_id, amount) VALUES (1, 100);

    SAVEPOINT sp1;
    INSERT INTO order_items (order_id, product_id) VALUES (1, 999);  -- might fail

    -- If it fails:
    ROLLBACK TO sp1;  -- undo only the last INSERT, keep the order

    -- Retry
    INSERT INTO order_items (order_id, product_id) VALUES (1, 1);
COMMIT;
```

## Isolation Levels

| Level | Prevents | Allows | Use Case |
|-------|----------|--------|----------|
| **READ COMMITTED** (default) | Dirty reads | Non-repeatable reads, phantoms | Most web apps |
| **REPEATABLE READ** | Dirty reads, non-repeatable reads, **phantoms** | Serialization anomalies | Reporting, snapshots |
| **SERIALIZABLE** | All anomalies | None (correctness) | Financial transactions |

```sql
-- Set isolation level
BEGIN ISOLATION LEVEL SERIALIZABLE;
    -- queries here are fully isolated
COMMIT;

-- Set for a session
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
```

> [!tip] When to use SERIALIZABLE
> Use `SERIALIZABLE` for financial transactions where correctness is critical. Be prepared to handle `40001: could not serialize access` errors by retrying the transaction.

## Locks

```sql
-- Pessimistic locking (select then update)
BEGIN;
    SELECT * FROM accounts WHERE id = 1 FOR UPDATE;  -- locks the row
    -- application computes new balance
    UPDATE accounts SET balance = 5000 WHERE id = 1;
COMMIT;  -- releases the lock
```

### Row-Level Lock Types

- `FOR UPDATE` — locks for update (blocks DELETE, other FOR UPDATE)
- `FOR NO KEY UPDATE` — weaker (allows FOR KEY SHARE)
- `FOR SHARE` — allows shares, blocks updates
- `FOR KEY SHARE` — weakest (only blocks DELETE)

## Deadlocks

```sql
-- Deadlock scenario:
-- Transaction A: UPDATE accounts SET ... WHERE id = 1; then id = 2
-- Transaction B: UPDATE accounts SET ... WHERE id = 2; then id = 1
-- Both wait for each other → deadlock
```

PostgreSQL detects deadlocks and aborts one transaction with `40P01: deadlock detected`.

> [!important] Prevent deadlocks
> Always lock resources in a **consistent order** across all transactions. If transaction A updates account 1 then 2, transaction B must also update 1 then 2 (not 2 then 1).

## Practice

```sql
-- Try a transaction
BEGIN;
    INSERT INTO employees (name, department, salary) VALUES ('Test', 'Engineering', 80000);
    SELECT * FROM employees WHERE name = 'Test';
    -- If happy: COMMIT; If not: ROLLBACK;
ROLLBACK;  -- undo the insert
SELECT * FROM employees WHERE name = 'Test';  -- should return 0 rows
```

## Next

- [[03-Intermediate-SQL/08-Constraints|Constraints]]
- [[04-Advanced-Topics/01-Performance-Tuning|Performance Tuning]]
