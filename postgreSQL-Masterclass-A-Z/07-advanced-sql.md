# 07 - Advanced SQL

> CTEs, recursive queries, window functions, subqueries, LATERAL, and modern SQL patterns.

---

## Common Table Expressions (CTEs)

```sql
WITH high_earners AS (
    SELECT id, first_name, last_name, salary, department_id
    FROM employees WHERE salary > 80000
)
SELECT h.first_name || ' ' || h.last_name AS employee, h.salary, d.name AS department
FROM high_earners h
JOIN departments d ON h.department_id = d.id;

-- Multiple CTEs
WITH 
    dept_stats AS (
        SELECT department_id, COUNT(*) AS emp_count, AVG(salary) AS avg_salary
        FROM employees GROUP BY department_id
    ),
    top_depts AS (
        SELECT department_id FROM dept_stats WHERE avg_salary > 70000
    )
SELECT e.first_name, e.last_name, e.salary
FROM employees e
JOIN top_depts td ON e.department_id = td.department_id;

-- Materialized CTE (computed once, reused)
WITH heavy_query AS MATERIALIZED (
    SELECT * FROM huge_table WHERE complex_condition = true
)
SELECT * FROM heavy_query h1
JOIN heavy_query h2 ON h1.id = h2.related_id;
```

---

## Recursive CTEs

```sql
-- Employee hierarchy
WITH RECURSIVE org_chart AS (
    -- Anchor: top-level managers
    SELECT id, first_name, last_name, manager_id, 1 AS level,
           first_name || ' ' || last_name AS path
    FROM employees WHERE manager_id IS NULL

    UNION ALL

    -- Recursive: subordinates
    SELECT e.id, e.first_name, e.last_name, e.manager_id, 
           oc.level + 1,
           oc.path || ' -> ' || e.first_name || ' ' || e.last_name
    FROM employees e
    JOIN org_chart oc ON e.manager_id = oc.id
)
SELECT REPEAT('  ', level - 1) || name AS name, level, path
FROM org_chart ORDER BY path;

-- Find all subordinates of a manager
WITH RECURSIVE subordinates AS (
    SELECT id, first_name, last_name, manager_id, 1 AS depth
    FROM employees WHERE id = 1
    UNION ALL
    SELECT e.id, e.first_name, e.last_name, e.manager_id, s.depth + 1
    FROM employees e JOIN subordinates s ON e.manager_id = s.id
)
SELECT * FROM subordinates WHERE depth > 1 ORDER BY depth;
```

---

## Window Functions

### ROW_NUMBER, RANK, DENSE_RANK

```sql
SELECT 
    first_name, last_name, salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num,
    RANK() OVER (ORDER BY salary DESC) AS rank_with_gaps,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank,
    ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS dept_rank
FROM employees;
```

### LAG / LEAD

```sql
SELECT 
    first_name, salary,
    LAG(salary, 1) OVER (ORDER BY salary) AS prev_salary,
    LEAD(salary, 1) OVER (ORDER BY salary) AS next_salary,
    salary - LAG(salary, 1) OVER (ORDER BY salary) AS diff
FROM employees ORDER BY salary;
```

### Running Totals & Moving Averages

```sql
SELECT 
    first_name, salary,
    SUM(salary) OVER (ORDER BY hire_date) AS running_total,
    AVG(salary) OVER (ORDER BY hire_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg
FROM employees ORDER BY hire_date;
```

### NTILE

```sql
SELECT first_name, salary,
    NTILE(4) OVER (ORDER BY salary) AS quartile,
    NTILE(10) OVER (ORDER BY salary) AS decile
FROM employees;
```

### FIRST_VALUE / LAST_VALUE

```sql
SELECT 
    department_id, first_name, salary,
    FIRST_VALUE(salary) OVER (PARTITION BY department_id ORDER BY salary) AS lowest,
    LAST_VALUE(salary) OVER (
        PARTITION BY department_id 
        ORDER BY salary 
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS highest
FROM employees;
```

---

## Subqueries

```sql
-- Scalar subquery
SELECT first_name, salary,
    (SELECT AVG(salary) FROM employees) AS company_avg,
    salary - (SELECT AVG(salary) FROM employees) AS diff
FROM employees;

-- Correlated subquery
SELECT e.first_name, e.salary,
    (SELECT AVG(salary) FROM employees WHERE department_id = e.department_id) AS dept_avg
FROM employees e;

-- EXISTS
SELECT d.name FROM departments d
WHERE EXISTS (SELECT 1 FROM employees e WHERE e.department_id = d.id);

-- NOT EXISTS
SELECT d.name FROM departments d
WHERE NOT EXISTS (SELECT 1 FROM employees e WHERE e.department_id = d.id);

-- IN / NOT IN
SELECT * FROM employees WHERE department_id IN (SELECT id FROM departments WHERE budget > 1000000);

-- LATERAL
SELECT d.name, top_earners.first_name, top_earners.salary
FROM departments d
LEFT JOIN LATERAL (
    SELECT first_name, salary FROM employees e
    WHERE e.department_id = d.id ORDER BY salary DESC LIMIT 2
) top_earners ON true;
```

---

## Modern SQL Patterns

### FILTER Clause

```sql
SELECT 
    department_id,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE is_active = TRUE) AS active,
    COUNT(*) FILTER (WHERE is_active = FALSE) AS inactive,
    AVG(salary) FILTER (WHERE hire_date > '2025-01-01') AS new_avg
FROM employees
GROUP BY department_id;
```

### DISTINCT ON

```sql
-- Most recent record per group
SELECT DISTINCT ON (department_id)
    department_id, first_name, last_name, salary, hire_date
FROM employees
ORDER BY department_id, hire_date DESC;
```

### Set Operations

```sql
-- UNION (distinct)
SELECT email FROM employees
UNION
SELECT email FROM customers;

-- UNION ALL (with duplicates)
SELECT email FROM employees
UNION ALL
SELECT email FROM customers;

-- INTERSECT
SELECT email FROM employees
INTERSECT
SELECT email FROM customers;

-- EXCEPT
SELECT email FROM employees
EXCEPT
SELECT email FROM customers;
```

---
*Previous: 06 - Indexes | Next: 08 - Transactions & Concurrency*
