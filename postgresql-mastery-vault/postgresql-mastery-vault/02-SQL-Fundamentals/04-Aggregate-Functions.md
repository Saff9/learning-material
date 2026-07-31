---
tags: [sql, fundamentals, aggregates, functions]
---

# Aggregate Functions

Aggregate functions compute a single result from a set of rows.

## Common Aggregates

```sql
-- COUNT: number of rows
SELECT COUNT(*) FROM users;                          -- total rows
SELECT COUNT(email) FROM users;                       -- non-NULL emails
SELECT COUNT(DISTINCT department) FROM employees;     -- unique departments

-- SUM: total
SELECT SUM(salary) FROM employees;
SELECT SUM(amount) AS total_revenue FROM orders WHERE status = 'paid';

-- AVG: average
SELECT AVG(salary) FROM employees;
SELECT AVG(price) FROM products WHERE category = 'electronics';

-- MIN and MAX
SELECT MIN(salary), MAX(salary) FROM employees;
SELECT MIN(created_at), MAX(created_at) FROM orders;

-- String aggregation (PostgreSQL-specific)
SELECT string_agg(name, ', ' ORDER BY name) FROM employees;
-- Result: "Alice, Bob, Carol, Dave, Eve, Frank"

-- Array aggregation
SELECT array_agg(name ORDER BY salary DESC) FROM employees;
-- Result: "{Frank, Alice, Bob, Carol, Dave, Eve}"
```

## Aggregates with NULL

```sql
-- COUNT(*) counts ALL rows (including NULLs)
-- COUNT(column) counts only non-NULL values
SELECT
    COUNT(*) AS total_rows,
    COUNT(phone) AS rows_with_phone
FROM users;

-- SUM, AVG, MIN, MAX ignore NULL values
SELECT AVG(price) FROM products;  -- NULL prices are skipped

-- COALESCE to handle NULLs
SELECT AVG(COALESCE(price, 0)) FROM products;  -- treat NULL as 0
```

## Aggregates with DISTINCT

```sql
SELECT COUNT(DISTINCT department) FROM employees;
SELECT SUM(DISTINCT price) FROM products;  -- sum of unique prices (rare but valid)
```

## Useful Aggregate Patterns

```sql
-- Count with a condition
SELECT
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE status = 'active') AS active,
    COUNT(*) FILTER (WHERE status = 'inactive') AS inactive
FROM users;

-- Percentage
SELECT
    COUNT(*) AS total,
    ROUND(
        COUNT(*) FILTER (WHERE is_active) * 100.0 / COUNT(*),
        2
    ) AS active_percentage
FROM users;

-- Multiple aggregates at once
SELECT
    department,
    COUNT(*) AS employee_count,
    ROUND(AVG(salary), 2) AS avg_salary,
    MIN(salary) AS min_salary,
    MAX(salary) AS max_salary,
    SUM(salary) AS total_payroll
FROM employees
GROUP BY department;
```

> [!tip] FILTER clause
> The `FILTER (WHERE ...)` clause is PostgreSQL-specific and cleaner than `CASE WHEN` for conditional aggregates. Use it!

## Statistical Aggregates

```sql
-- Percentile (requires extension or built-in in newer versions)
SELECT
    percentile_cont(0.5) WITHIN GROUP (ORDER BY salary) AS median,
    percentile_cont(0.95) WITHIN GROUP (ORDER BY salary) AS p95
FROM employees;

-- Standard deviation
SELECT stddev(salary), variance(salary) FROM employees;

-- Mode (most frequent value)
SELECT mode() WITHIN GROUP (ORDER BY department) FROM employees;
```

## Practice

```sql
-- Total payroll
SELECT SUM(salary) AS total_payroll FROM employees;

-- Average salary by department (requires GROUP BY)
SELECT department, AVG(salary) FROM employees GROUP BY department;

-- How many employees were hired each year?
SELECT EXTRACT(YEAR FROM hire_date) AS year, COUNT(*) AS hires
FROM employees
GROUP BY year
ORDER BY year;
```

## Next

- [[02-SQL-Fundamentals/05-GROUP-BY-HAVING|GROUP BY and HAVING]]
- [[02-SQL-Fundamentals/06-JOINS|JOINs]]
