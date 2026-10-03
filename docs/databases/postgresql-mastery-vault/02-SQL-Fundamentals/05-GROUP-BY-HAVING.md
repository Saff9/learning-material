---
tags: [sql, fundamentals, group-by, having]
---

# GROUP BY and HAVING

`GROUP BY` groups rows that share the same values. `HAVING` filters groups (like WHERE for groups).

## GROUP BY Basics

```sql
-- Count employees per department
SELECT department, COUNT(*) AS employee_count
FROM employees
GROUP BY department;

-- Average salary per department
SELECT department, ROUND(AVG(salary), 2) AS avg_salary
FROM employees
GROUP BY department
ORDER BY avg_salary DESC;

-- Multiple columns
SELECT department, job_title, COUNT(*) AS count
FROM employees
GROUP BY department, job_title
ORDER BY department, job_title;
```

## HAVING — Filter Groups

```sql
-- Departments with more than 3 employees
SELECT department, COUNT(*) AS employee_count
FROM employees
GROUP BY department
HAVING COUNT(*) > 3;

-- Departments with average salary > 70000
SELECT department, AVG(salary) AS avg_salary
FROM employees
GROUP BY department
HAVING AVG(salary) > 70000
ORDER BY avg_salary DESC;

-- Multiple conditions
SELECT department, COUNT(*) AS count, AVG(salary) AS avg_salary
FROM employees
GROUP BY department
HAVING COUNT(*) > 2 AND AVG(salary) > 70000;
```

## WHERE vs HAVING

> [!important] WHERE filters rows BEFORE grouping. HAVING filters groups AFTER grouping.

```sql
-- WHERE filters individual rows first, then GROUP BY groups them, then HAVING filters groups
SELECT department, COUNT(*) AS count, AVG(salary) AS avg_salary
FROM employees
WHERE salary > 50000          -- filter individual employees first
GROUP BY department           -- then group
HAVING AVG(salary) > 70000;   -- then filter groups
```

## Clause Evaluation Order

```
FROM → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT
```

1. **FROM**: Identify the table(s)
2. **WHERE**: Filter individual rows
3. **GROUP BY**: Group the remaining rows
4. **HAVING**: Filter groups
5. **SELECT**: Choose columns and compute expressions
6. **DISTINCT**: Remove duplicate rows
7. **ORDER BY**: Sort
8. **LIMIT/OFFSET**: Paginate

## GROUP BY with Multiple Aggregates

```sql
SELECT
    department,
    COUNT(*) AS employee_count,
    ROUND(AVG(salary), 2) AS avg_salary,
    MIN(salary) AS min_salary,
    MAX(salary) AS max_salary,
    SUM(salary) AS total_payroll
FROM employees
GROUP BY department
ORDER BY total_payroll DESC;
```

## GROUP BY with Date/Time

```sql
-- Orders per day
SELECT DATE(created_at) AS order_date, COUNT(*) AS orders
FROM orders
GROUP BY order_date
ORDER BY order_date;

-- Revenue per month
SELECT
    DATE_TRUNC('month', created_at) AS month,
    COUNT(*) AS order_count,
    SUM(amount) AS revenue
FROM orders
GROUP BY month
ORDER BY month;

-- Revenue per hour of day
SELECT
    EXTRACT(HOUR FROM created_at) AS hour,
    COUNT(*) AS orders,
    SUM(amount) AS revenue
FROM orders
GROUP BY hour
ORDER BY hour;
```

## GROUP BY ROLLUP and CUBE

```sql
-- ROLLUP: adds subtotals and a grand total
SELECT department, COUNT(*) AS count
FROM employees
GROUP BY ROLLUP (department);
-- Returns: each department count + NULL (grand total)

-- CUBE: all possible subtotals
SELECT department, job_title, COUNT(*) AS count
FROM employees
GROUP BY CUBE (department, job_title);
-- Returns: every combination + subtotals + grand total
```

## GROUPING SETS

```sql
-- Specify exactly which groupings you want
SELECT department, job_title, COUNT(*) AS count
FROM employees
GROUP BY GROUPING SETS (
    (department, job_title),  -- per dept+title
    (department),              -- per dept only
    ()                         -- grand total
);
```

## Practice

```sql
-- How many employees in each department?
SELECT department, COUNT(*) FROM employees GROUP BY department;

-- Which departments have average salary > 80000?
SELECT department, AVG(salary)
FROM employees
GROUP BY department
HAVING AVG(salary) > 80000;

-- Revenue per month in 2026
SELECT DATE_TRUNC('month', created_at) AS month, SUM(amount)
FROM orders
WHERE created_at >= '2026-01-01'
GROUP BY month
ORDER BY month;
```

## Next

- [[02-SQL-Fundamentals/06-JOINS|JOINs]] — combine tables
- [[02-SQL-Fundamentals/07-Subqueries|Subqueries]]
