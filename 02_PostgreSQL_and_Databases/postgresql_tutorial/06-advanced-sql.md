# 06 - Advanced SQL

## Common Table Expressions (CTEs)

CTEs create temporary result sets that can be referenced within a query. They improve readability and enable recursion.

### Basic CTEs

```sql
-- Simple CTE
WITH high_earners AS (
    SELECT id, first_name, last_name, salary, department_id
    FROM employees
    WHERE salary > 80000
)
SELECT 
    h.first_name || ' ' || h.last_name AS employee,
    h.salary,
    d.name AS department
FROM high_earners h
JOIN departments d ON h.department_id = d.id;

-- Multiple CTEs
WITH 
    dept_stats AS (
        SELECT 
            department_id,
            COUNT(*) AS emp_count,
            AVG(salary) AS avg_salary
        FROM employees
        GROUP BY department_id
    ),
    top_depts AS (
        SELECT department_id
        FROM dept_stats
        WHERE avg_salary > 70000
    )
SELECT 
    e.first_name,
    e.last_name,
    e.salary,
    d.name AS department
FROM employees e
JOIN top_depts td ON e.department_id = td.department_id
JOIN departments d ON e.department_id = d.id
ORDER BY e.salary DESC;
```

### Recursive CTEs

Essential for hierarchical data (org charts, tree structures, paths).

```sql
-- Employee hierarchy (who reports to whom)
WITH RECURSIVE employee_hierarchy AS (
    -- Anchor: Start with top-level managers (no manager)
    SELECT 
        id, 
        first_name, 
        last_name, 
        manager_id, 
        1 AS level,
        first_name || ' ' || last_name AS path
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive: Find subordinates
    SELECT 
        e.id,
        e.first_name,
        e.last_name,
        e.manager_id,
        eh.level + 1,
        eh.path || ' -> ' || e.first_name || ' ' || e.last_name
    FROM employees e
    INNER JOIN employee_hierarchy eh ON e.manager_id = eh.id
)
SELECT 
    id,
    REPEAT('  ', level - 1) || first_name || ' ' || last_name AS name,
    level,
    path
FROM employee_hierarchy
ORDER BY path;

-- Result:
-- Alice Johnson        | 1 | Alice Johnson
--   Bob Smith          | 2 | Alice Johnson -> Bob Smith
--     Carol Davis      | 3 | Alice Johnson -> Bob Smith -> Carol Davis
--     David Wilson     | 3 | Alice Johnson -> Bob Smith -> David Wilson
--   Eve Brown          | 2 | Alice Johnson -> Eve Brown
--     Frank Miller     | 3 | Alice Johnson -> Eve Brown -> Frank Miller
--     ...
```

```sql
-- Find all subordinates of a specific manager
WITH RECURSIVE subordinates AS (
    SELECT id, first_name, last_name, manager_id, 1 AS depth
    FROM employees
    WHERE id = 1  -- Alice (CEO)

    UNION ALL

    SELECT e.id, e.first_name, e.last_name, e.manager_id, s.depth + 1
    FROM employees e
    JOIN subordinates s ON e.manager_id = s.id
)
SELECT * FROM subordinates WHERE depth > 1 ORDER BY depth;

-- Bill of materials (product components)
WITH RECURSIVE components AS (
    SELECT id, name, parent_id, quantity, 1 AS level
    FROM parts
    WHERE parent_id IS NULL

    UNION ALL

    SELECT p.id, p.name, p.parent_id, p.quantity, c.level + 1
    FROM parts p
    JOIN components c ON p.parent_id = c.id
)
SELECT REPEAT('  ', level - 1) || name AS component, quantity
FROM components
ORDER BY level, name;
```

---

## Window Functions

Window functions perform calculations across a set of rows related to the current row. They do not collapse rows like GROUP BY.

### ROW_NUMBER, RANK, DENSE_RANK

```sql
-- Row numbering
SELECT 
    first_name,
    last_name,
    salary,
    department_id,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS overall_rank,
    ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS dept_rank
FROM employees;

-- Ranking with ties
SELECT 
    first_name,
    last_name,
    salary,
    RANK() OVER (ORDER BY salary DESC) AS rank_with_gaps,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS rank_no_gaps,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS unique_rank
FROM employees;

-- Difference between them:
-- salary | RANK | DENSE_RANK | ROW_NUMBER
-- 95000  | 1    | 1          | 1
-- 85000  | 2    | 2          | 2
-- 80000  | 3    | 3          | 3
-- 80000  | 3    | 3          | 4   ← tie!
-- 75000  | 5    | 4          | 5   ← RANK skips 4
```

### LAG and LEAD

Access data from previous or next rows.

```sql
-- Compare current salary with previous employee
SELECT 
    first_name,
    last_name,
    salary,
    LAG(salary, 1) OVER (ORDER BY salary) AS prev_salary,
    LEAD(salary, 1) OVER (ORDER BY salary) AS next_salary,
    salary - LAG(salary, 1) OVER (ORDER BY salary) AS diff_from_prev,
    LEAD(salary, 1) OVER (ORDER BY salary) - salary AS diff_to_next
FROM employees
ORDER BY salary;

-- Compare with previous in same department
SELECT 
    department_id,
    first_name,
    salary,
    LAG(salary, 1) OVER (PARTITION BY department_id ORDER BY salary) AS prev_in_dept,
    salary - LAG(salary, 1) OVER (PARTITION BY department_id ORDER BY salary) AS gap
FROM employees
ORDER BY department_id, salary;

-- First and last value in group
SELECT 
    department_id,
    first_name,
    salary,
    FIRST_VALUE(salary) OVER (PARTITION BY department_id ORDER BY salary) AS lowest_in_dept,
    LAST_VALUE(salary) OVER (
        PARTITION BY department_id 
        ORDER BY salary 
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS highest_in_dept
FROM employees;
```

### Running Totals and Moving Averages

```sql
-- Running total of salaries
SELECT 
    first_name,
    salary,
    SUM(salary) OVER (ORDER BY hire_date) AS running_total,
    AVG(salary) OVER (ORDER BY hire_date) AS running_avg
FROM employees
ORDER BY hire_date;

-- Moving average (3-row window)
SELECT 
    hire_date,
    salary,
    AVG(salary) OVER (
        ORDER BY hire_date 
        ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
    ) AS moving_avg_3,
    SUM(salary) OVER (
        ORDER BY hire_date 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS sum_last_3
FROM employees
ORDER BY hire_date;

-- Percent of total
SELECT 
    department_id,
    first_name,
    salary,
    SUM(salary) OVER (PARTITION BY department_id) AS dept_total,
    ROUND(salary::NUMERIC / SUM(salary) OVER (PARTITION BY department_id) * 100, 2) AS pct_of_dept,
    SUM(salary) OVER () AS company_total,
    ROUND(salary::NUMERIC / SUM(salary) OVER () * 100, 2) AS pct_of_company
FROM employees;
```

### Window Frame Specifications

```sql
-- Frame types
SELECT 
    id,
    salary,
    -- All rows from start to current
    SUM(salary) OVER (ORDER BY id ROWS UNBOUNDED PRECEDING) AS cumsum,

    -- Current row and 2 before
    SUM(salary) OVER (ORDER BY id ROWS 2 PRECEDING) AS sum_3_rows,

    -- All rows in partition (same as SUM without ORDER BY)
    SUM(salary) OVER (PARTITION BY department_id) AS dept_total,

    -- Range (all rows with same ORDER BY value)
    SUM(salary) OVER (ORDER BY hire_date RANGE UNBOUNDED PRECEDING) AS range_sum,

    -- Between specific rows
    AVG(salary) OVER (
        ORDER BY hire_date 
        ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
    ) AS avg_5_row_window
FROM employees;
```

### NTILE

Divide rows into equal buckets.

```sql
-- Quartiles
SELECT 
    first_name,
    salary,
    NTILE(4) OVER (ORDER BY salary) AS quartile,
    NTILE(10) OVER (ORDER BY salary) AS decile,
    CASE NTILE(4) OVER (ORDER BY salary)
        WHEN 1 THEN 'Bottom 25%'
        WHEN 2 THEN '25-50%'
        WHEN 3 THEN '50-75%'
        WHEN 4 THEN 'Top 25%'
    END AS salary_bracket
FROM employees;
```

---

## Subqueries

### Scalar Subqueries

Return a single value.

```sql
-- Employees earning above average
SELECT first_name, last_name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);

-- Correlated subquery
SELECT e.first_name, e.salary, e.department_id,
    (SELECT AVG(salary) FROM employees WHERE department_id = e.department_id) AS dept_avg
FROM employees e;
```

### IN and NOT IN

```sql
-- Employees in specific departments
SELECT * FROM employees
WHERE department_id IN (SELECT id FROM departments WHERE budget > 1000000);

-- Employees NOT in any project
SELECT * FROM employees
WHERE id NOT IN (SELECT DISTINCT employee_id FROM employee_projects);

-- Better alternative (handles NULLs correctly)
SELECT * FROM employees e
WHERE NOT EXISTS (SELECT 1 FROM employee_projects ep WHERE ep.employee_id = e.id);
```

### EXISTS and NOT EXISTS

```sql
-- Departments with employees
SELECT d.name
FROM departments d
WHERE EXISTS (SELECT 1 FROM employees e WHERE e.department_id = d.id);

-- Departments without employees
SELECT d.name
FROM departments d
WHERE NOT EXISTS (SELECT 1 FROM employees e WHERE e.department_id = d.id);

-- Employees working on multiple projects
SELECT e.first_name
FROM employees e
WHERE (SELECT COUNT(*) FROM employee_projects ep WHERE ep.employee_id = e.id) > 2;
```

### ANY / ALL

```sql
-- Salary greater than ANY in department 1
SELECT * FROM employees
WHERE salary > ANY (SELECT salary FROM employees WHERE department_id = 1);

-- Salary greater than ALL in department 1
SELECT * FROM employees
WHERE salary > ALL (SELECT salary FROM employees WHERE department_id = 1);

-- Equivalent to:
SELECT * FROM employees
WHERE salary > (SELECT MAX(salary) FROM employees WHERE department_id = 1);
```

### LATERAL Subqueries

```sql
-- LATERAL allows subquery to reference columns from preceding FROM items
SELECT 
    d.name AS department,
    top_earners.first_name,
    top_earners.salary
FROM departments d
LEFT JOIN LATERAL (
    SELECT first_name, salary
    FROM employees e
    WHERE e.department_id = d.id
    ORDER BY salary DESC
    LIMIT 2
) top_earners ON true;

-- Without LATERAL (would be an error):
-- SELECT d.name, e.first_name FROM departments d, 
-- (SELECT first_name FROM employees WHERE department_id = d.id) e;  -- ERROR!
```

---

## Set Operations

### UNION

Combine results, removing duplicates.

```sql
-- All unique email addresses from two tables
SELECT email FROM employees
UNION
SELECT email FROM customers;

-- UNION ALL keeps duplicates (faster)
SELECT email FROM employees
UNION ALL
SELECT email FROM customers;
```

### INTERSECT

Return rows common to both queries.

```sql
-- Emails present in both tables
SELECT email FROM employees
INTERSECT
SELECT email FROM customers;
```

### EXCEPT

Return rows in first query but not second.

```sql
-- Employee emails not in customers
SELECT email FROM employees
EXCEPT
SELECT email FROM customers;

-- With ALL to keep duplicates
SELECT email FROM employees
EXCEPT ALL
SELECT email FROM customers;
```

---

## Pivoting and Unpivoting

### Crosstab (Pivot)

```sql
-- Install tablefunc extension
CREATE EXTENSION IF NOT EXISTS tablefunc;

-- Pivot: departments as columns, count as values
SELECT * FROM crosstab(
    'SELECT department_id, is_active, COUNT(*) 
     FROM employees 
     GROUP BY department_id, is_active 
     ORDER BY 1, 2',
    'SELECT DISTINCT is_active FROM employees ORDER BY 1'
) AS ct(department_id INT, active_count BIGINT, inactive_count BIGINT);
```

### Manual Pivot with CASE

```sql
-- Pivot with CASE
SELECT 
    department_id,
    COUNT(CASE WHEN is_active = TRUE THEN 1 END) AS active_count,
    COUNT(CASE WHEN is_active = FALSE THEN 1 END) AS inactive_count,
    COUNT(*) AS total
FROM employees
GROUP BY department_id;

-- Pivot salary ranges
SELECT 
    department_id,
    COUNT(CASE WHEN salary < 60000 THEN 1 END) AS "<60k",
    COUNT(CASE WHEN salary BETWEEN 60000 AND 80000 THEN 1 END) AS "60k-80k",
    COUNT(CASE WHEN salary > 80000 THEN 1 END) AS ">80k"
FROM employees
GROUP BY department_id;
```

### Unpivot

```sql
-- Convert columns to rows
WITH unpivoted AS (
    SELECT department_id, 'active' AS status, 
           COUNT(CASE WHEN is_active = TRUE THEN 1 END) AS count
    FROM employees GROUP BY department_id
    UNION ALL
    SELECT department_id, 'inactive' AS status, 
           COUNT(CASE WHEN is_active = FALSE THEN 1 END) AS count
    FROM employees GROUP BY department_id
)
SELECT * FROM unpivoted WHERE count > 0 ORDER BY department_id, status;
```

---

## Advanced Filtering

### FILTER Clause

```sql
-- Conditional aggregation without CASE
SELECT 
    department_id,
    COUNT(*) AS total_employees,
    COUNT(*) FILTER (WHERE is_active = TRUE) AS active_count,
    COUNT(*) FILTER (WHERE is_active = FALSE) AS inactive_count,
    AVG(salary) FILTER (WHERE is_active = TRUE) AS active_avg_salary,
    AVG(salary) FILTER (WHERE hire_date > '2023-01-01') AS new_hire_avg
FROM employees
GROUP BY department_id;
```

### DISTINCT ON

```sql
-- Get the most recent record per group (PostgreSQL specific)
SELECT DISTINCT ON (department_id)
    department_id,
    first_name,
    last_name,
    salary,
    hire_date
FROM employees
ORDER BY department_id, hire_date DESC;
-- Returns one row per department (most recently hired)
```

### LIMIT WITH TIES

```sql
-- Get top 3 salaries, including ties
SELECT * FROM employees
ORDER BY salary DESC
FETCH FIRST 3 ROWS WITH TIES;
-- If 3rd and 4th have same salary, both are returned
```

### TABLESAMPLE

```sql
-- Random sample of rows
SELECT * FROM employees TABLESAMPLE SYSTEM (10);
-- Returns approximately 10% of rows (fast, block-level)

SELECT * FROM employees TABLESAMPLE BERNOULLI (10);
-- Returns exactly 10% probability per row (slower, row-level, more random)

SELECT * FROM employees TABLESAMPLE SYSTEM (10) REPEATABLE (42);
-- Reproducible sample with seed 42
```

---

## Summary

| Feature | Purpose |
|---------|---------|
| **CTEs** | Readable temporary result sets |
| **Recursive CTEs** | Hierarchical/tree queries |
| **Window Functions** | Row-by-row calculations without grouping |
| **Subqueries** | Nested queries for complex logic |
| **LATERAL** | Correlated subqueries in FROM clause |
| **Set Operations** | UNION, INTERSECT, EXCEPT |
| **Pivot/Unpivot** | Transform row/column orientation |
| **FILTER** | Conditional aggregation |
| **DISTINCT ON** | First row per group |
| **TABLESAMPLE** | Random sampling |

---
*Previous: [05 - Constraints & Indexes](05-constraints-indexes.md) | Next: [07 - Transactions & ACID](07-transactions-acid.md)*
