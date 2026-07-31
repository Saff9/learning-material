# 10 - Triggers & Event Triggers

> Row-level, statement-level, INSTEAD OF triggers, and DDL event triggers.

---

## Row-Level Triggers

```sql
-- Auto-update timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_employees_updated_at
    BEFORE UPDATE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Audit log
CREATE OR REPLACE FUNCTION log_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (table_name, action, record_id, old_data, new_data)
    VALUES (TG_TABLE_NAME, TG_OP, COALESCE(NEW.id, OLD.id), 
            row_to_json(OLD), row_to_json(NEW));
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_employees
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION log_changes();

-- Soft delete (archive before delete)
CREATE OR REPLACE FUNCTION archive_before_delete()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO employees_archive SELECT OLD.*, NOW();
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_archive_employee
    BEFORE DELETE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION archive_before_delete();
```

---

## Statement-Level Triggers

```sql
CREATE OR REPLACE FUNCTION notify_change()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('table_changes', json_build_object(
        'table', TG_TABLE_NAME, 'op', TG_OP, 'time', NOW()
    )::TEXT);
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_notify
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH STATEMENT
    EXECUTE FUNCTION notify_change();
```

---

## INSTEAD OF Triggers (Views)

```sql
CREATE VIEW employee_department_view AS
SELECT e.id, e.first_name, e.last_name, e.email, d.id AS dept_id, d.name AS dept_name
FROM employees e JOIN departments d ON e.department_id = d.id;

CREATE OR REPLACE FUNCTION insert_employee_view()
RETURNS TRIGGER AS $$
DECLARE new_dept_id INTEGER;
BEGIN
    INSERT INTO departments (name) VALUES (NEW.dept_name)
    ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
    RETURNING id INTO new_dept_id;

    INSERT INTO employees (first_name, last_name, email, department_id)
    VALUES (NEW.first_name, NEW.last_name, NEW.email, new_dept_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_insert_emp_view
    INSTEAD OF INSERT ON employee_department_view
    FOR EACH ROW EXECUTE FUNCTION insert_employee_view();
```

---

## Event Triggers (DDL)

```sql
CREATE OR REPLACE FUNCTION log_ddl()
RETURNS EVENT_TRIGGER AS $$
BEGIN
    INSERT INTO ddl_log (event_type, object_type, object_name, command, executed_at)
    SELECT TG_EVENT, TG_OBJECT_TYPE, TG_OBJECT_IDENTITY, TG_TAG, NOW();
END;
$$ LANGUAGE plpgsql;

CREATE EVENT TRIGGER trg_log_ddl ON ddl_command_end
    EXECUTE FUNCTION log_ddl();

-- Specific events only
CREATE EVENT TRIGGER trg_log_tables ON ddl_command_end
    WHEN TAG IN ('CREATE TABLE', 'ALTER TABLE', 'DROP TABLE')
    EXECUTE FUNCTION log_ddl();
```

---

## Trigger Control

```sql
-- Disable/Enable
ALTER TABLE employees DISABLE TRIGGER trg_employees_updated_at;
ALTER TABLE employees ENABLE TRIGGER trg_employees_updated_at;
ALTER TABLE employees DISABLE TRIGGER ALL;  -- All triggers
ALTER TABLE employees ENABLE TRIGGER ALL;

-- Conditional trigger
CREATE TRIGGER trg_high_salary_alert
    AFTER INSERT OR UPDATE OF salary ON employees
    FOR EACH ROW WHEN (NEW.salary > 100000)
    EXECUTE FUNCTION notify_high_salary();
```

---
*Previous: 09 - Functions | Next: 11 - JSON & JSONB*
