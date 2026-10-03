# 14 - Views & Materialized Views

> Virtual tables, updatable views, recursive views, materialized views, and continuous aggregations.

---

## Views

Views in PostgreSQL are essentially stored queries. They don't store data themselves (unlike Materialized Views) but execute their underlying query every time they are accessed.

```sql
-- Simple view
CREATE OR REPLACE VIEW employee_details AS
SELECT 
    e.id, e.first_name || ' ' || e.last_name AS full_name,
    e.email, e.salary, d.name AS department
FROM employees e JOIN departments d ON e.department_id = d.id;

-- Query view
SELECT * FROM employee_details WHERE department = 'Engineering';

-- View with aggregation
CREATE OR REPLACE VIEW department_summary AS
SELECT 
    d.id, d.name,
    COUNT(e.id) AS emp_count,
    AVG(e.salary) AS avg_salary
FROM departments d LEFT JOIN employees e ON d.id = e.department_id
GROUP BY d.id, d.name;

-- Security view (hide sensitive columns)
-- Views are highly useful for row-level/column-level security implementations
CREATE VIEW public_employees AS
SELECT id, first_name, last_name, department_id, hire_date
FROM employees;
```

---

## Updatable Views

PostgreSQL automatically makes views updatable (INSERT, UPDATE, DELETE) if they meet specific criteria (usually, they must reference a single table and contain no aggregations, groupings, or set operations).

```sql
-- Simple view is auto-updatable
CREATE VIEW active_employees AS SELECT * FROM employees WHERE is_active = TRUE;

-- LOCAL vs CASCADED CHECK OPTION
-- WITH LOCAL CHECK OPTION: only checks conditions defined directly on this view
-- WITH CASCADED CHECK OPTION (default): checks conditions on this view AND all underlying views

CREATE VIEW active_employees_safe AS 
SELECT * FROM employees WHERE is_active = TRUE
WITH CASCADED CHECK OPTION;
-- INSERT into active_employees_safe (is_active) VALUES (FALSE); -- WILL FAIL

-- Complex view needs INSTEAD OF trigger
CREATE VIEW employee_dept_view AS
SELECT e.id, e.first_name, d.name AS dept_name
FROM employees e JOIN departments d ON e.department_id = d.id;

-- Trigger function to handle writes to the complex view
CREATE OR REPLACE FUNCTION insert_emp_dept()
RETURNS TRIGGER AS $$
DECLARE did INTEGER;
BEGIN
    -- Handle Department
    INSERT INTO departments (name) VALUES (NEW.dept_name) ON CONFLICT (name) DO NOTHING;
    SELECT id INTO did FROM departments WHERE name = NEW.dept_name;
    
    -- Handle Employee
    IF TG_OP = 'INSERT' THEN
        INSERT INTO employees (first_name, department_id) VALUES (NEW.first_name, did);
    ELSIF TG_OP = 'UPDATE' THEN
        UPDATE employees SET first_name = NEW.first_name, department_id = did WHERE id = OLD.id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_insert_emp_dept
    INSTEAD OF INSERT OR UPDATE ON employee_dept_view
    FOR EACH ROW EXECUTE FUNCTION insert_emp_dept();
```

---

## Recursive Views

Recursive views are syntactic sugar around Recursive CTEs (Common Table Expressions). They are phenomenal for querying hierarchical data like org charts, file systems, or graphs.

```sql
CREATE OR REPLACE RECURSIVE VIEW org_chart (id, name, manager_id, level, path) AS
-- Base case (Anchor member)
SELECT id, first_name || ' ' || last_name AS name, manager_id, 1 AS level, 
       first_name || ' ' || last_name AS path
FROM employees WHERE manager_id IS NULL
UNION ALL
-- Recursive case
SELECT e.id, e.first_name || ' ' || e.last_name, e.manager_id, oc.level + 1,
       oc.path || ' > ' || e.first_name || ' ' || e.last_name
FROM employees e JOIN org_chart oc ON e.manager_id = oc.id;

-- Query the recursive view
SELECT * FROM org_chart ORDER BY path;
```

---

## Materialized Views

Materialized views store the physical result set of their query. This trades off data freshness for absolute read performance.

```sql
-- Create Materialized View
CREATE MATERIALIZED VIEW mv_department_stats AS
SELECT d.id, d.name, COUNT(e.id) AS emp_count, AVG(e.salary) AS avg_salary
FROM departments d LEFT JOIN employees e ON d.id = e.department_id
GROUP BY d.id, d.name
WITH DATA; -- WITH NO DATA creates the structure but leaves it empty until refreshed

-- Query (Extremely fast, essentially querying a normal table!)
SELECT * FROM mv_department_stats WHERE avg_salary > 70000;

-- Create index on MV (Highly recommended)
-- A unique index is REQUIRED if you want to refresh concurrently
CREATE UNIQUE INDEX idx_mv_dept_id ON mv_department_stats(id);

-- Refresh Strategies

-- Standard Refresh (blocks ALL reads to the MV while refreshing)
REFRESH MATERIALIZED VIEW mv_department_stats;

-- Concurrent Refresh (does NOT block reads, updates data in background)
-- Calculates the diff between old and new data, requiring a unique index to identify rows.
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_department_stats;
```

### Automation & Continuous Aggregates

PostgreSQL does not natively auto-refresh Materialized Views. You must schedule them via `pg_cron`, external crontabs, or application workers.

```sql
-- Example using pg_cron to refresh every night at 3 AM
SELECT cron.schedule('0 3 * * *', 'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_department_stats');
```

For time-series data, consider using **TimescaleDB Continuous Aggregates**, which are auto-updating materialized views optimized for time-based data.

---

## When to Use What

| Feature | Regular View | Materialized View |
|---------|-------------|-------------------|
| **Storage** | None (Query only) | Physical data on disk |
| **Speed** | Depends completely on query | Extremely fast (pre-computed) |
| **Freshness** | 100% Real-time | Stale until manually refreshed |
| **Indexes** | Defined on base tables | Defined on the MV itself |
| **Writable** | Automatically or via Triggers | **Never** |
| **Best For** | Security, Query simplification, Abstraction | Dashboards, Heavy analytics, Caching |

---
*Previous: 13 - Full-Text Search | Next: 15 - Partitioning*
