# 14 - Views & Materialized Views

> Virtual tables, updatable views, recursive views, and materialized views.

---

## Views

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
CREATE VIEW public_employees AS
SELECT id, first_name, last_name, department_id, hire_date
FROM employees;
```

---

## Updatable Views

```sql
-- Simple view is auto-updatable
CREATE VIEW active_employees AS SELECT * FROM employees WHERE is_active = TRUE;

-- With CHECK OPTION
CREATE VIEW active_employees AS SELECT * FROM employees WHERE is_active = TRUE
WITH CHECK OPTION;
-- INSERT with is_active = FALSE will fail

-- Complex view needs INSTEAD OF trigger
CREATE VIEW employee_dept_view AS
SELECT e.id, e.first_name, d.name AS dept_name
FROM employees e JOIN departments d ON e.department_id = d.id;

CREATE OR REPLACE FUNCTION insert_emp_dept()
RETURNS TRIGGER AS $$
DECLARE did INTEGER;
BEGIN
    INSERT INTO departments (name) VALUES (NEW.dept_name) ON CONFLICT (name) DO NOTHING;
    SELECT id INTO did FROM departments WHERE name = NEW.dept_name;
    INSERT INTO employees (first_name, department_id) VALUES (NEW.first_name, did);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_insert_emp_dept
    INSTEAD OF INSERT ON employee_dept_view
    FOR EACH ROW EXECUTE FUNCTION insert_emp_dept();
```

---

## Recursive Views

```sql
CREATE OR REPLACE RECURSIVE VIEW org_chart AS
SELECT id, first_name || ' ' || last_name AS name, manager_id, 1 AS level, 
       first_name || ' ' || last_name AS path
FROM employees WHERE manager_id IS NULL
UNION ALL
SELECT e.id, e.first_name || ' ' || e.last_name, e.manager_id, oc.level + 1,
       oc.path || ' > ' || e.first_name || ' ' || e.last_name
FROM employees e JOIN org_chart oc ON e.manager_id = oc.id;
```

---

## Materialized Views

```sql
-- Create
CREATE MATERIALIZED VIEW mv_department_stats AS
SELECT d.id, d.name, COUNT(e.id) AS emp_count, AVG(e.salary) AS avg_salary
FROM departments d LEFT JOIN employees e ON d.id = e.department_id
GROUP BY d.id, d.name;

-- Query (fast!)
SELECT * FROM mv_department_stats WHERE avg_salary > 70000;

-- Create index on MV
CREATE UNIQUE INDEX idx_mv_dept_id ON mv_department_stats(id);

-- Refresh (blocks reads)
REFRESH MATERIALIZED VIEW mv_department_stats;

-- Concurrent refresh (needs unique index, no locks)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_department_stats;
```

---

## When to Use What

| Feature | View | Materialized View |
|---------|------|-------------------|
| Storage | Query only | Physical data |
| Speed | Depends on query | Fast (pre-computed) |
| Freshness | Real-time | Stale until refresh |
| Indexes | On base tables | On MV itself |
| Writable | Sometimes | Never |

---
*Previous: 13 - Full-Text Search | Next: 15 - Partitioning*
