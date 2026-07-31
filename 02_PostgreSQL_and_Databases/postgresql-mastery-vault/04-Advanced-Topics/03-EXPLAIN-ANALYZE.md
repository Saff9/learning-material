---
tags: [postgresql, advanced, explain, query-plan]
---

# EXPLAIN and EXPLAIN ANALYZE

`EXPLAIN` shows the query plan. `EXPLAIN ANALYZE` executes the query and shows actual timings.

## Basic Usage

```sql
-- Show estimated plan (doesn't execute)
EXPLAIN SELECT * FROM users WHERE email = 'alice@example.com';

-- Execute and show actual timings
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'alice@example.com';

-- With I/O details
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM users WHERE email = 'alice@example.com';

-- Full detail
EXPLAIN (ANALYZE, BUFFERS, VERBOSE) SELECT * FROM users WHERE email = 'alice@example.com';
```

## Reading the Plan

The output is a tree — read it **bottom-up** (inside-out).

```
Limit (cost=1234.56..1234.58 rows=10 width=72) (actual time=45.2..45.3 rows=10 loops=1)
  ->  Sort (cost=1234.56..1250.00 rows=6175 width=72) (actual time=45.1..45.2 rows=10 loops=1)
        Sort Key: (sum(o.total_amount)) DESC
        ->  HashAggregate (cost=1100.00..1180.00 rows=6175 width=72) (actual time=38..42 rows=5900 loops=1)
              ->  Hash Join (cost=4.50..980.00 rows=12000 width=72) (actual time=0.1..30 rows=12000 loops=1)
                    ->  Seq Scan on orders o (actual time=0.01..15 rows=12000 loops=1)
                    ->  Hash (cost=3.00..3.00 rows=100) (actual time=0.05 rows=100 loops=1)
                          ->  Seq Scan on customers c (actual time=0.01..0.03 rows=100 loops=1)
```

## Key Metrics

- **cost=0.00..42.10** — startup cost..total cost (arbitrary units, ~sequential page fetches)
- **rows=1000** — estimated (or actual) rows returned
- **width=64** — average row width in bytes
- **actual time=0.012..0.089** — startup..total time in ms (only with ANALYZE)
- **loops=1** — how many times this node was executed
- **shared hit=42 read=8** — cache hits vs disk reads (with BUFFERS)

## Scan Types

| Scan | Meaning | When |
|------|---------|------|
| **Seq Scan** | Read entire table | Small table, or no useful index |
| **Index Scan** | Walk B-tree, fetch heap tuples | Selective query on indexed column |
| **Index Only Scan** | Answer from index alone | All columns in index + all-visible pages |
| **Bitmap Index Scan** | Build bitmap of matching TIDs, then fetch | Moderate selectivity |

> [!note] Index Scan is not always faster than Seq Scan
> For low-selectivity queries (matching 30%+ of rows), a sequential scan + sort can be cheaper than thousands of random index lookups.

## Join Methods

| Join | How | Best for |
|------|-----|----------|
| **Nested Loop** | For each outer row, scan inner | Small outer + indexed inner |
| **Hash Join** | Build hash table on smaller input | Medium/large, equality joins |
| **Merge Join** | Both inputs sorted, merge | Large pre-sorted inputs |

## Signs of Trouble

- **Rows Removed by Filter is huge** → missing index
- **Estimated vs actual rows wildly differ** → run ANALYZE
- **Nested Loop with Seq Scan on inner** → O(N*M) blowup, needs index
- **Sort spilling to disk** → increase work_mem
- **Hash Batches > 1** → hash spilled, increase work_mem

## Practice

```sql
-- Compare with and without an index
EXPLAIN ANALYZE SELECT * FROM employees WHERE department = 'Engineering';

CREATE INDEX idx_emp_dept ON employees(department);

EXPLAIN ANALYZE SELECT * FROM employees WHERE department = 'Engineering';
-- Should now show Index Scan instead of Seq Scan
```

## Next

- [[04-Advanced-Topics/04-Partitioning|Partitioning]]
- [[04-Advanced-Topics/06-JSON-JSONB|JSON/JSONB]]
