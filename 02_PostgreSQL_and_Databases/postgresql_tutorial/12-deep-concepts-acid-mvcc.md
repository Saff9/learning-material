# Deep Dive: ACID, Transaction Isolation, and MVCC

## 1. Relational Database Theory Core Concepts
At the heart of PostgreSQL is the relational model. Data is stored in tables (relations) consisting of rows (tuples) and columns (attributes). The key theoretical foundation ensures data integrity through normalization and constraints (Primary Keys, Foreign Keys).

## 2. ACID Properties
ACID guarantees that database transactions are processed reliably:
* **Atomicity**: "All or nothing." A transaction is a single indivisible unit. If a part of it fails, the entire transaction fails, and the database state is left unchanged.
* **Consistency**: A transaction must transform the database from one valid state to another valid state, maintaining all constraints and triggers.
* **Isolation**: Concurrent execution of transactions leaves the database in the same state that would have been obtained if the transactions were executed sequentially.
* **Durability**: Once a transaction has been committed, it will remain committed even in the case of a system failure (e.g., power loss). PostgreSQL ensures this using the Write-Ahead Log (WAL).

## 3. Transaction Isolation Levels in PostgreSQL
PostgreSQL implements different levels of isolation to balance performance and strictness:

### Read Committed (Default)
A query only sees data committed before the query began. It never sees uncommitted data or changes committed by concurrent transactions during the query's execution.
* **Phenomena allowed**: Non-repeatable reads, Phantom reads.

### Repeatable Read
All queries in the current transaction only see rows committed before the *transaction* began (not just the query).
* **Phenomena prevented**: Non-repeatable reads.
* **Note**: In PostgreSQL, Repeatable Read also prevents Phantom reads (unlike standard SQL definitions).

### Serializable
The strictest level. It emulates serial transaction execution for all committed transactions; as if transactions had been executed one after another, serially, rather than concurrently. If a concurrent transaction violates this, PostgreSQL rolls it back with a serialization failure error.

## 4. Multi-Version Concurrency Control (MVCC)
MVCC is how PostgreSQL handles concurrency. Instead of locking a row when reading it, PostgreSQL maintains multiple versions of the row.
* Each transaction sees a "snapshot" of the database at a specific point in time.
* When a row is updated, a new version of the row is created (the old version is kept for concurrent transactions that might still need it).
* This means **readers never block writers, and writers never block readers**.
* **Vacuuming**: The `VACUUM` process cleans up old row versions (dead tuples) that are no longer visible to any active transaction, reclaiming space.
