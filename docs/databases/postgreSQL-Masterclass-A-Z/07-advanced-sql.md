# 07 - Advanced SQL

> CTEs, recursive queries, window functions, subqueries, LATERAL joins, table partitioning, advanced indexing (pgvector), and modern PostgreSQL patterns.

---

## Common Table Expressions (CTEs)

Common Table Expressions (CTEs) allow you to write named subqueries that can be referenced within a larger query. This greatly enhances readability and modularity. 

**Under the Hood (PostgreSQL 12+):** Historically, CTEs acted as "optimizer fences", meaning PostgreSQL evaluated them independently and materialized the result before running the outer query. Since PG 12, CTEs are **inlined** by default if they are side-effect-free and only referenced once. This allows the query planner to push down filters into the CTE.

```sql
-- Standard CTE
WITH high_earners AS (
    SELECT id, first_name, last_name, salary, department_id
    FROM employees 
    WHERE salary > 80000
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
```

### Controlling CTE Materialization

You can explicitly override the planner's default behavior using `MATERIALIZED` or `NOT MATERIALIZED`.

```sql
-- Force materialization (computed once, reused, creates an optimizer fence)
WITH heavy_query AS MATERIALIZED (
    SELECT * FROM huge_table WHERE complex_condition = true
)
SELECT * FROM heavy_query h1
JOIN heavy_query h2 ON h1.id = h2.related_id;

-- Force inlining (even if referenced multiple times)
WITH quick_calc AS NOT MATERIALIZED (
    SELECT id, value * 1.5 AS adjusted_value FROM factors
)
SELECT * FROM quick_calc;
```

---

## Recursive CTEs

Recursive CTEs are essential for querying hierarchical data (e.g., organizational charts, folder structures, bill of materials). 

**Architecture:** A recursive CTE executes the *anchor member* first, then repeatedly executes the *recursive member*, joining against the working table from the previous iteration, until no rows are returned.

```sql
-- Employee hierarchy
WITH RECURSIVE org_chart AS (
    -- Anchor: top-level managers
    SELECT id, first_name, last_name, manager_id, 1 AS level,
           ARRAY[id] AS path_array,
           first_name || ' ' || last_name AS path
    FROM employees WHERE manager_id IS NULL

    UNION ALL

    -- Recursive: subordinates
    SELECT e.id, e.first_name, e.last_name, e.manager_id, 
           oc.level + 1,
           oc.path_array || e.id,
           oc.path || ' -> ' || e.first_name || ' ' || e.last_name
    FROM employees e
    JOIN org_chart oc ON e.manager_id = oc.id
)
SELECT REPEAT('  ', level - 1) || name AS name, level, path
FROM org_chart ORDER BY path_array;
```

### Advanced: Cycle Detection
In PostgreSQL 14+, you can handle infinite loops cleanly using the `CYCLE` clause, which prevents infinite recursion if your graph data has loops.

```sql
WITH RECURSIVE graph_search AS (
    SELECT id, linked_id FROM nodes WHERE id = 1
    UNION ALL
    SELECT n.id, n.linked_id 
    FROM nodes n JOIN graph_search gs ON n.id = gs.linked_id
) SEARCH DEPTH FIRST BY id SET order_seq
CYCLE id SET is_cycle USING path
SELECT * FROM graph_search;
```

---

## Window Functions

Window functions perform calculations across a set of table rows that are related to the current row, without grouping them into a single output row.

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

### Advanced Framing: ROWS vs RANGE

Window frames dictate the subset of rows used for calculations. Understanding the default behavior is crucial: `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`.

```sql
SELECT 
    first_name, salary, hire_date,
    -- ROWS: strictly positional (exactly 2 rows before)
    AVG(salary) OVER (ORDER BY hire_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg,
    -- RANGE: logical (all rows with the same hire_date value as the current row)
    SUM(salary) OVER (ORDER BY hire_date RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM employees ORDER BY hire_date;
```

### Lead, Lag & Distribution

```sql
SELECT 
    first_name, salary,
    LAG(salary, 1) OVER (ORDER BY salary) AS prev_salary,
    LEAD(salary, 1) OVER (ORDER BY salary) AS next_salary,
    CUME_DIST() OVER (ORDER BY salary) AS cumulative_distribution,
    PERCENT_RANK() OVER (ORDER BY salary) AS percentile
FROM employees ORDER BY salary;
```

---

## Subqueries & LATERAL Joins

### Scalar & Correlated Subqueries
A correlated subquery references columns from the outer query. While flexible, they can be slow because they execute once per row of the outer query.

```sql
-- Correlated subquery
SELECT e.first_name, e.salary,
    (SELECT AVG(salary) FROM employees WHERE department_id = e.department_id) AS dept_avg
FROM employees e;
```

### The LATERAL Keyword
`LATERAL` acts like a "for each" loop in SQL. It allows a subquery in the `FROM` clause to access columns from preceding tables. It's incredibly powerful for fetching "Top-N" records per group or expanding JSON arrays.

```sql
-- Fetch the top 2 highest paid employees per department
SELECT d.name, top_earners.first_name, top_earners.salary
FROM departments d
LEFT JOIN LATERAL (
    SELECT first_name, salary FROM employees e
    WHERE e.department_id = d.id 
    ORDER BY salary DESC LIMIT 2
) top_earners ON true;

-- Unnesting JSONB arrays using LATERAL
SELECT p.id, t.tag
FROM products p
CROSS JOIN LATERAL jsonb_array_elements_text(p.tags) AS t(tag);
```

---

## Advanced PostgreSQL Topics & Architecture

### Table Partitioning
Partitioning splits large tables into smaller, manageable logical pieces. PostgreSQL supports Range, List, and Hash partitioning natively. This dramatically improves performance for large datasets via **Partition Pruning**.

```sql
-- Create a parent partitioned table
CREATE TABLE sensor_data (
    id serial,
    device_id int,
    reading numeric,
    created_at timestamp
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE sensor_data_y2023m01 PARTITION OF sensor_data
    FOR VALUES FROM ('2023-01-01') TO ('2023-02-01');

CREATE TABLE sensor_data_y2023m02 PARTITION OF sensor_data
    FOR VALUES FROM ('2023-02-01') TO ('2023-03-01');
```
*Note: Make sure `enable_partition_pruning = on` in your config so Postgres skips scanning irrelevant partitions.*

### Query Planning Optimization
To truly write advanced SQL, you must measure it. `EXPLAIN` shows the execution plan, but `EXPLAIN (ANALYZE, BUFFERS)` actually runs the query and shows real timing and memory usage.

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT * FROM employees WHERE salary > 100000;
```
Look for `Seq Scan` (Sequential Scans) on large tables, which indicates a missing index, and check `shared hit` vs `read` in buffers to see if data is coming from RAM or Disk.

### Advanced Indexing: GIN & pgvector
PostgreSQL's extensibility allows specialized indexing:

```sql
-- GIN Index for rapid JSONB querying
CREATE INDEX idx_products_metadata ON products USING GIN (metadata jsonb_path_ops);

-- Searching within JSONB
SELECT * FROM products WHERE metadata @> '{"color": "red"}';

-- pgvector for AI/ML embeddings (Nearest Neighbor Search)
CREATE EXTENSION vector;
CREATE TABLE items (id bigserial, embedding vector(3));
CREATE INDEX ON items USING hnsw (embedding vector_l2_ops);

-- Find top 5 closest items by L2 distance
SELECT * FROM items ORDER BY embedding <-> '[1,2,3]' LIMIT 5;
```

### Row-Level Security (RLS)
RLS enforces security constraints directly in the database. When enabled, users can only read/write rows that pass a security policy. Highly useful for multi-tenant SaaS applications.

```sql
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON tenants
    USING (tenant_id = current_setting('app.current_tenant_id')::int);

-- Users query the table normally, but Postgres implicitly appends the WHERE clause.
SELECT * FROM tenants; 
```

---

## Modern SQL Patterns

### FILTER Clause
The `FILTER` clause is the modern, readable replacement for `SUM(CASE WHEN...)`.

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
Extracts the first row of each group based on an `ORDER BY` clause. Often much faster than using window functions for simple "get the latest record" queries.

```sql
-- Most recent salary review per employee
SELECT DISTINCT ON (employee_id)
    employee_id, new_salary, review_date
FROM salary_history
ORDER BY employee_id, review_date DESC;
```

### GROUPING SETS, CUBE, and ROLLUP
For advanced aggregations (pivot tables/subtotals) in a single query pass.

```sql
SELECT department_id, job_title, SUM(salary)
FROM employees
GROUP BY ROLLUP (department_id, job_title);
-- Produces subtotals for each department, and a grand total at the end.
```

---
*Previous: 06 - Indexes | Next: 08 - Transactions & Concurrency*
