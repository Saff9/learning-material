# Advanced SQL Query Guide

## 1. Advanced JOINs
Beyond `INNER` and `LEFT` JOINs:
* **FULL OUTER JOIN**: Returns all records when there is a match in either left or right table.
* **CROSS JOIN**: Returns the Cartesian product of the sets of records from the two joined tables.
* **LATERAL JOIN**: A powerful feature that allows a subquery in the `FROM` clause to reference columns from preceding items in the `FROM` list. Useful for top-N queries per group.

## 2. Common Table Expressions (CTEs) & WITH RECURSIVE
CTEs make complex queries readable by breaking them into simpler blocks.
```sql
WITH regional_sales AS (
    SELECT region, SUM(amount) AS total_sales
    FROM orders GROUP BY region
)
SELECT * FROM regional_sales WHERE total_sales > 10000;
```

**WITH RECURSIVE**: Used for querying hierarchical data (e.g., organizational charts, graphs).
```sql
WITH RECURSIVE employee_hierarchy AS (
    -- Base case
    SELECT id, name, manager_id, 1 AS depth
    FROM employees WHERE manager_id IS NULL
    UNION ALL
    -- Recursive step
    SELECT e.id, e.name, e.manager_id, eh.depth + 1
    FROM employees e
    JOIN employee_hierarchy eh ON e.manager_id = eh.id
)
SELECT * FROM employee_hierarchy;
```

## 3. Window Functions
Perform calculations across a set of table rows that are related to the current row, without collapsing them into a single output row.

* **ROW_NUMBER()**: Assigns a unique sequential integer to rows within a partition.
* **RANK()**: Assigns a rank to rows, with gaps in rank values if there are ties.
* **DENSE_RANK()**: Like RANK(), but no gaps.
* **LEAD(col, offset)**: Accesses data from a subsequent row in the same result set.
* **LAG(col, offset)**: Accesses data from a previous row.

```sql
SELECT employee_id, salary,
       LAG(salary, 1) OVER (ORDER BY hire_date) as prev_hire_salary,
       RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as dept_salary_rank
FROM employees;
```

## 4. JSONB Operations
PostgreSQL's `jsonb` type stores JSON data in a decomposed binary format, allowing fast indexing and querying.
* Extracting values: `->` (returns JSON), `->>` (returns text).
* Extracting path: `#>` (returns JSON), `#>>` (returns text).
* Containment: `@>` checks if the left JSON value contains the right.
* Key existence: `?` checks if a string exists as a top-level key.

```sql
-- Find all users whose details contain {"plan": "premium"}
SELECT * FROM users WHERE details @> '{"plan": "premium"}';
```
