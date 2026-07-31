---
tags: [sql, fundamentals, order-by, limit, pagination]
---

# ORDER BY and LIMIT

## ORDER BY

```sql
-- Single column, ascending (default)
SELECT * FROM employees ORDER BY salary;

-- Single column, descending
SELECT * FROM employees ORDER BY salary DESC;

-- Multiple columns
SELECT * FROM employees ORDER BY department ASC, salary DESC;

-- By column position (not recommended — fragile)
SELECT name, salary FROM employees ORDER BY 2 DESC;

-- By expression
SELECT name, salary FROM employees ORDER BY salary * 12 DESC;

-- NULL handling
SELECT * FROM products ORDER BY price DESC NULLS LAST;  -- NULLs at end
SELECT * FROM products ORDER BY price DESC NULLS FIRST; -- NULLs at start
```

> [!note] NULLS LAST is PostgreSQL default for ASC, NULLS FIRST for DESC
> This means NULLs sort as if they were the largest values. Use `NULLS LAST` explicitly for clarity.

## LIMIT and OFFSET

```sql
-- First 10 rows
SELECT * FROM users ORDER BY created_at DESC LIMIT 10;

-- Skip first 20, get next 10 (page 3)
SELECT * FROM users ORDER BY created_at DESC LIMIT 10 OFFSET 20;

-- SQL-standard syntax
SELECT * FROM users ORDER BY created_at DESC
OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY;

-- No limit, just offset (rare)
SELECT * FROM users ORDER BY created_at DESC OFFSET 5;
```

## Pagination Pattern

```sql
-- Page 1: items 1-10
SELECT id, name FROM products ORDER BY id LIMIT 10 OFFSET 0;

-- Page 2: items 11-20
SELECT id, name FROM products ORDER BY id LIMIT 10 OFFSET 10;
```

### Keyset Pagination (Better for Large Tables)

> [!important] OFFSET is slow for large offsets
> `OFFSET 100000` means PostgreSQL scans and discards 100,000 rows. For large tables, use **keyset pagination** instead:

```sql
-- First page
SELECT id, name FROM products ORDER BY id LIMIT 10;

-- Next page: use the last ID from the previous page
SELECT id, name FROM products WHERE id > 100 ORDER BY id LIMIT 10;
-- (where 100 is the last ID from page 1)
```

Keyset pagination is O(log n) instead of O(n) — dramatically faster for deep pages.

## Practice

```sql
-- Get the top 3 highest-paid employees
SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 3;

-- Get page 2 of 5-per-page results
SELECT name, salary FROM employees ORDER BY id LIMIT 5 OFFSET 5;

-- Get the 3 lowest-paid employees
SELECT name, salary FROM employees ORDER BY salary ASC LIMIT 3;
```

## Next

- [[02-SQL-Fundamentals/04-Aggregate-Functions|Aggregate Functions]]
- [[02-SQL-Fundamentals/05-GROUP-BY-HAVING|GROUP BY and HAVING]]
