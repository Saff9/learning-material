---
tags: [sql, intermediate, cte, with-clause]
---

# Common Table Expressions (CTEs)

CTEs (WITH clauses) create temporary named result sets that make complex queries readable.

## Basic CTE

```sql
WITH high_earners AS (
    SELECT department_id, COUNT(*) AS cnt, AVG(salary) AS avg_sal
    FROM employees
    WHERE salary > 80000
    GROUP BY department_id
)
SELECT d.name, h.cnt, h.avg_sal
FROM high_earners h
JOIN departments d ON d.id = h.department_id
ORDER BY h.avg_sal DESC;
```

## Multiple CTEs

```sql
WITH
active_users AS (
    SELECT id, name FROM users WHERE is_active = true
),
user_orders AS (
    SELECT user_id, COUNT(*) AS order_count, SUM(amount) AS total_spent
    FROM orders
    GROUP BY user_id
)
SELECT au.name, uo.order_count, uo.total_spent
FROM active_users au
LEFT JOIN user_orders uo ON uo.user_id = au.id
ORDER BY uo.total_spent DESC NULLS LAST;
```

## Data Modification with CTEs

```sql
-- Move old records to archive
WITH moved AS (
    DELETE FROM orders WHERE created_at < '2025-01-01'
    RETURNING *
)
INSERT INTO orders_archive
SELECT * FROM moved;
```

## MATERIALIZED vs NOT MATERIALIZED

```sql
-- MATERIALIZED: CTE is computed once and cached (good for expensive queries used multiple times)
WITH expensive AS MATERIALIZED (
    SELECT user_id, SUM(amount) AS total FROM orders GROUP BY user_id
)
SELECT * FROM expensive WHERE total > 1000;

-- NOT MATERIALIZED: CTE is inlined (good for simple queries)
WITH simple AS NOT MATERIALIZED (
    SELECT * FROM users WHERE is_active = true
)
SELECT * FROM simple WHERE name LIKE 'A%';
```

> [!note] PostgreSQL 12+ inlines CTEs by default
> Before PostgreSQL 12, CTEs were always materialized (an optimization fence). Since PG 12, non-recursive CTEs are inlined by default. Use `MATERIALIZED` to force caching.

## Practice

```sql
-- Find departments where average salary is above company average
WITH dept_avg AS (
    SELECT department_id, AVG(salary) AS avg_sal
    FROM employees GROUP BY department_id
),
company_avg AS (
    SELECT AVG(salary) AS avg_sal FROM employees
)
SELECT d.name, da.avg_sal
FROM dept_avg da
JOIN departments d ON d.id = da.department_id
CROSS JOIN company_avg ca
WHERE da.avg_sal > ca.avg_sal;
```

## Next

- [[03-Intermediate-SQL/03-Recursive-Queries|Recursive Queries]]
- [[03-Intermediate-SQL/06-Indexes|Indexes]]
