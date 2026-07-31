# 10 - Views & Materialized Views

## Views

A **view** is a virtual table based on a query. It doesn't store data — it stores the query definition.

```
┌─────────────────────────────────────────────┐
│                    VIEW                       │
│                                              │
│   ┌──────────────┐    ┌──────────────┐       │
│   │   employees  │    │ departments│       │
│   │──────────────│    │──────────────│       │
│   │ id           │    │ id           │       │
│   │ name         │    │ name         │       │
│   │ dept_id      │───►│ id           │       │
│   │ salary       │    │ budget       │       │
│   └──────────────┘    └──────────────┘       │
│          │                                   │
│          ▼                                   │
│   ┌──────────────────────────────────┐      │
│   │ CREATE VIEW employee_details AS  │      │
│   │ SELECT e.*, d.name as dept_name│      │
│   │ FROM employees e               │      │
│   │ JOIN departments d ON ...      │      │
│   └──────────────────────────────────┘      │
│          │                                   │
│          ▼                                   │
│   ┌──────────────────────────────────┐      │
│   │ SELECT * FROM employee_details   │      │
│   │ (runs the underlying query)      │      │
│   └──────────────────────────────────┘      │
└─────────────────────────────────────────────┘
```

### Creating Views

```sql
-- Simple view
CREATE OR REPLACE VIEW employee_details AS
SELECT 
    e.id,
    e.first_name || ' ' || e.last_name AS full_name,
    e.email,
    e.salary,
    d.name AS department,
    d.location,
    m.first_name || ' ' || m.last_name AS manager
FROM employees e
JOIN departments d ON e.department_id = d.id
LEFT JOIN employees m ON e.manager_id = m.id;

-- Query the view
SELECT * FROM employee_details WHERE department = 'Engineering';

-- View with aggregation
CREATE OR REPLACE VIEW department_summary AS
SELECT 
    d.id AS department_id,
    d.name AS department_name,
    COUNT(e.id) AS employee_count,
    COALESCE(AVG(e.salary), 0) AS average_salary,
    COALESCE(SUM(e.salary), 0) AS total_payroll,
    MIN(e.hire_date) AS earliest_hire,
    MAX(e.hire_date) AS latest_hire
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id
GROUP BY d.id, d.name;

-- View with security (hide sensitive columns)
CREATE OR REPLACE VIEW public_employees AS
SELECT 
    id,
    first_name,
    last_name,
    department_id,
    hire_date
FROM employees;
-- Salary and email are hidden!
```

### Updatable Views

```sql
-- Simple view (automatically updatable)
CREATE OR REPLACE VIEW active_employees AS
SELECT * FROM employees WHERE is_active = TRUE;

-- Insert through view
INSERT INTO active_employees (first_name, last_name, email, salary)
VALUES ('New', 'Employee', 'new@company.com', 60000);
-- Automatically sets is_active = TRUE? No! Need trigger or check constraint.

-- With check option (prevent inserting rows that wouldn't appear in view)
CREATE OR REPLACE VIEW active_employees AS
SELECT * FROM employees WHERE is_active = TRUE
WITH CHECK OPTION;
-- Now: INSERT with is_active = FALSE will fail!

-- Local vs Cascaded check option
CREATE OR REPLACE VIEW v1 AS SELECT * FROM t WHERE a > 0 WITH LOCAL CHECK OPTION;
CREATE OR REPLACE VIEW v2 AS SELECT * FROM v1 WHERE b > 0 WITH CASCADED CHECK OPTION;
-- LOCAL: Only checks v1's condition
-- CASCADED: Checks v1 AND v2's conditions
```

### Views with Triggers (Complex Updatable Views)

```sql
-- Complex view (joins multiple tables)
CREATE OR REPLACE VIEW employee_department_view AS
SELECT 
    e.id,
    e.first_name,
    e.last_name,
    e.email,
    e.salary,
    d.id AS department_id,
    d.name AS department_name,
    d.location AS department_location
FROM employees e
JOIN departments d ON e.department_id = d.id;

-- Make it updatable with INSTEAD OF triggers
CREATE OR REPLACE FUNCTION employee_department_view_insert()
RETURNS TRIGGER AS $$
DECLARE
    new_dept_id INTEGER;
BEGIN
    -- Insert or get department
    INSERT INTO departments (name, location)
    VALUES (NEW.department_name, NEW.department_location)
    ON CONFLICT (name) DO UPDATE SET location = EXCLUDED.location
    RETURNING id INTO new_dept_id;

    -- Insert employee
    INSERT INTO employees (first_name, last_name, email, salary, department_id)
    VALUES (NEW.first_name, NEW.last_name, NEW.email, NEW.salary, new_dept_id);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_insert_employee_dept_view
    INSTEAD OF INSERT ON employee_department_view
    FOR EACH ROW
    EXECUTE FUNCTION employee_department_view_insert();

-- Now you can insert into the view!
INSERT INTO employee_department_view (first_name, last_name, email, salary, department_name, department_location)
VALUES ('Zoe', 'Martinez', 'zoe@company.com', 70000, 'Research', 'Building D');
```

### Recursive Views

```sql
-- Recursive view for org chart
CREATE OR REPLACE RECURSIVE VIEW org_chart AS
    -- Base case: top-level employees
    SELECT 
        id,
        first_name || ' ' || last_name AS name,
        manager_id,
        1 AS level,
        first_name || ' ' || last_name AS path
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive case: subordinates
    SELECT 
        e.id,
        e.first_name || ' ' || e.last_name,
        e.manager_id,
        oc.level + 1,
        oc.path || ' > ' || e.first_name || ' ' || e.last_name
    FROM employees e
    JOIN org_chart oc ON e.manager_id = oc.id;

SELECT * FROM org_chart ORDER BY path;
```

---

## Materialized Views

A **materialized view** stores the query result physically. It is fast to query but must be refreshed.

```
┌─────────────────────────────────────────────┐
│           MATERIALIZED VIEW                  │
│                                              │
│   ┌──────────────┐    ┌──────────────┐       │
│   │   employees  │    │ departments  │       │
│   └──────────────┘    └──────────────┘       │
│          │                                   │
│          ▼                                   │
│   ┌──────────────────────────────────┐      │
│   │ CREATE MATERIALIZED VIEW mv AS │      │
│   │ SELECT ... FROM employees e    │      │
│   │ JOIN departments d ON ...      │      │
│   └──────────────────────────────────┘      │
│          │                                   │
│          ▼                                   │
│   ┌──────────────────────────────────┐      │
│   │ PHYSICALLY STORED RESULT SET     │      │
│   │ (like a table, with indexes)     │      │
│   └──────────────────────────────────┘      │
│                                              │
│   SELECT * FROM mv -- Instant! No query      │
│   REFRESH MATERIALIZED VIEW mv -- Update     │
└─────────────────────────────────────────────┘
```

### Creating Materialized Views

```sql
-- Basic materialized view
CREATE MATERIALIZED VIEW mv_department_stats AS
SELECT 
    d.id AS department_id,
    d.name AS department_name,
    COUNT(e.id) AS employee_count,
    AVG(e.salary) AS avg_salary,
    SUM(e.salary) AS total_salary
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id
GROUP BY d.id, d.name;

-- Query it (fast!)
SELECT * FROM mv_department_stats WHERE avg_salary > 70000;

-- Create with index
CREATE MATERIALIZED VIEW mv_employee_search AS
SELECT 
    e.id,
    e.first_name || ' ' || e.last_name AS full_name,
    e.email,
    d.name AS department,
    to_tsvector('english', 
        coalesce(e.first_name, '') || ' ' ||
        coalesce(e.last_name, '') || ' ' ||
        coalesce(e.email, '') || ' ' ||
        coalesce(d.name, '')
    ) AS search_vector
FROM employees e
JOIN departments d ON e.department_id = d.id;

-- Create index on materialized view
CREATE INDEX idx_mv_employee_search ON mv_employee_search USING gin(search_vector);
```

### Refreshing Materialized Views

```sql
-- Full refresh (blocks reads)
REFRESH MATERIALIZED VIEW mv_department_stats;

-- Concurrent refresh (no locks, requires unique index)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_department_stats;

-- To enable concurrent refresh, you need a unique index:
CREATE UNIQUE INDEX idx_mv_dept_stats_id ON mv_department_stats(department_id);
-- Now concurrent refresh works!

-- Refresh in a transaction
BEGIN;
REFRESH MATERIALIZED VIEW mv_department_stats;
COMMIT;

-- Check last refresh time
SELECT 
    schemaname, 
    matviewname, 
    hasindexes, 
    ispopulated
FROM pg_matviews 
WHERE matviewname = 'mv_department_stats';
```

### When to Use Materialized Views

| Use Case | View | Materialized View |
|----------|------|-------------------|
| Real-time data | ✓ | ✗ |
| Complex aggregations on large data | Slow | ✓ Fast |
| Data that changes infrequently | ✓ | ✓ |
| Reporting dashboards | Slow | ✓ Fast |
| Full-text search | Slow | ✓ Fast |
| Data warehousing | ✗ | ✓ |

### Materialized View Refresh Strategies

```sql
-- Manual refresh (on-demand)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_department_stats;

-- Scheduled refresh (using pg_cron extension)
CREATE EXTENSION IF NOT EXISTS pg_cron;
SELECT cron.schedule('refresh-mv', '0 2 * * *', 
    'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_department_stats');

-- Trigger-based refresh
CREATE OR REPLACE FUNCTION refresh_mv_department_stats()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_department_stats;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_refresh_mv
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_mv_department_stats();
-- Note: This can cause performance issues with high write volume!
```

---

## View Security

### Ownership and Security

```sql
-- Create view with security barrier (prevent optimization attacks)
CREATE OR REPLACE VIEW employee_public WITH (security_barrier) AS
SELECT id, first_name, last_name, department_id
FROM employees
WHERE is_active = TRUE;

-- Security invoker vs definer
CREATE OR REPLACE VIEW employee_sensitive WITH (security_invoker) AS
SELECT * FROM employees;
-- Runs with caller's permissions

-- Change owner
ALTER VIEW employee_details OWNER TO admin_user;

-- Grant/revoke on views
GRANT SELECT ON employee_public TO app_readonly;
REVOKE ALL ON employee_details FROM public;
```

---

## Summary

| Feature | View | Materialized View |
|---------|------|-------------------|
| Storage | Query only | Physical data |
| Query Speed | Depends on underlying query | Fast (pre-computed) |
| Data Freshness | Real-time | Stale until refresh |
| Indexes | On underlying tables | On materialized view |
| Writeable | Sometimes (simple views) | Never |
| Concurrent Refresh | N/A | Yes (with unique index) |

---
*Previous: [09 - JSON & JSONB](09-json-jsonb.md) | Next: [11 - Performance Tuning](11-performance-tuning.md)*
