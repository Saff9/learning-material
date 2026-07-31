# 10 - Triggers & Event Triggers

> Row-level, statement-level, INSTEAD OF triggers, and DDL event triggers. A deep dive into PostgreSQL trigger architecture, execution models, and advanced use cases.

---

## The PostgreSQL Trigger Architecture

Triggers in PostgreSQL are callbacks that are executed automatically when specified events occur on a table or view. They can be fired `BEFORE`, `AFTER`, or `INSTEAD OF` a DML operation (`INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`), and can act at either the statement level (`FOR EACH STATEMENT`) or row level (`FOR EACH ROW`).

**Key Architectural Considerations:**
- **Performance Impact:** Row-level triggers execute a function for every affected row. For bulk operations (e.g., `COPY` or mass `UPDATE`s), this can cause significant overhead. Consider statement-level triggers where bulk operations are frequent.
- **Execution Order:** Triggers are fired in alphabetical order of their names. Naming conventions (e.g., `01_trg_before_insert`, `02_trg_before_insert`) are critical to guaranteeing deterministic execution flow.
- **Transaction Safety:** Triggers execute within the same transaction as the triggering statement. If the trigger raises an exception, the entire transaction is rolled back.

---

## Row-Level Triggers

Row-level triggers provide granular control over data manipulation. They can modify data before it hits the table or act on it right after.

### Auto-Update Timestamp & Data Validation

Using a `BEFORE` trigger to manage audit columns like `updated_at` ensures the database is the source of truth, rather than relying on application code.

```sql
-- Create a generic function that can be reused across tables
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    -- Prevent overriding updated_at explicitly by the user
    IF NEW.updated_at IS DISTINCT FROM OLD.updated_at THEN
        RAISE EXCEPTION 'Cannot manually update updated_at';
    END IF;

    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_employees_set_updated_at
    BEFORE UPDATE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();
```

### Advanced Audit Logging (JSONB & System Metadata)

A robust audit logging mechanism captures not just the changes but also session context.

```sql
-- Secure Audit Table
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    action TEXT NOT NULL,
    record_id TEXT,
    old_data JSONB,
    new_data JSONB,
    changed_by_user TEXT DEFAULT current_user,
    client_ip INET DEFAULT inet_client_addr(),
    changed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit log function utilizing JSONB for flexible storage
CREATE OR REPLACE FUNCTION audit_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO audit_log (table_name, action, record_id, old_data)
        VALUES (TG_TABLE_NAME, TG_OP, OLD.id::TEXT, to_jsonb(OLD));
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO audit_log (table_name, action, record_id, old_data, new_data)
        VALUES (TG_TABLE_NAME, TG_OP, NEW.id::TEXT, to_jsonb(OLD), to_jsonb(NEW));
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO audit_log (table_name, action, record_id, new_data)
        VALUES (TG_TABLE_NAME, TG_OP, NEW.id::TEXT, to_jsonb(NEW));
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
-- Using SECURITY DEFINER allows logging even if the user lacks INSERT grants on audit_log

CREATE TRIGGER trg_audit_employees
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION audit_changes();
```

*Best Practice:* Use `SECURITY DEFINER` carefully. It executes with the privileges of the function's creator. Always pair it with strict schema qualification (e.g., setting `search_path`) to prevent search path hijacking.

---

## Statement-Level Triggers

Statement-level triggers fire once per operation, regardless of how many rows are affected (even zero rows). They are ideal for summary operations, materialized view refreshes, or pub/sub notifications via `NOTIFY`.

### Transition Tables (Advanced Feature)

PostgreSQL 10 introduced Transition Tables (`REFERENCING NEW TABLE AS ... OLD TABLE AS ...`), allowing statement-level triggers to access the set of affected rows efficiently without per-row overhead.

```sql
CREATE OR REPLACE FUNCTION audit_bulk_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- Record all inserted rows in a single bulk insert
    INSERT INTO audit_log (table_name, action, new_data)
    SELECT TG_TABLE_NAME, TG_OP, to_jsonb(n)
    FROM new_table n;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_bulk_employees
    AFTER INSERT ON employees
    REFERENCING NEW TABLE AS new_table
    FOR EACH STATEMENT
    EXECUTE FUNCTION audit_bulk_changes();
```

---

## INSTEAD OF Triggers (Updatable Views)

Complex views involving joins or aggregates are not automatically updatable. `INSTEAD OF` triggers allow you to define exactly how DML operations on the view should translate to the underlying base tables.

```sql
CREATE VIEW employee_department_view AS
SELECT e.id, e.first_name, e.last_name, e.email, d.id AS dept_id, d.name AS dept_name
FROM employees e JOIN departments d ON e.department_id = d.id;

CREATE OR REPLACE FUNCTION maintain_employee_view()
RETURNS TRIGGER AS $$
DECLARE
    v_dept_id INTEGER;
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- Handle Department
        SELECT id INTO v_dept_id FROM departments WHERE name = NEW.dept_name;
        IF NOT FOUND THEN
            INSERT INTO departments (name) VALUES (NEW.dept_name) RETURNING id INTO v_dept_id;
        END IF;

        -- Handle Employee
        INSERT INTO employees (first_name, last_name, email, department_id)
        VALUES (NEW.first_name, NEW.last_name, NEW.email, v_dept_id);
        RETURN NEW;
        
    ELSIF TG_OP = 'UPDATE' THEN
        -- Complex update logic involving both tables
        -- ...
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_maintain_emp_view
    INSTEAD OF INSERT OR UPDATE ON employee_department_view
    FOR EACH ROW EXECUTE FUNCTION maintain_employee_view();
```

---

## Event Triggers (DDL Triggers)

Event triggers fire on Data Definition Language (DDL) events globally across the database. They are powerful for enforcing naming conventions, auditing schema changes, or replicating DDL in multi-tenant environments.

### Advanced DDL Auditing and Enforcement

```sql
CREATE OR REPLACE FUNCTION enforce_naming_conventions()
RETURNS EVENT_TRIGGER AS $$
DECLARE
    obj RECORD;
BEGIN
    FOR obj IN SELECT * FROM pg_event_trigger_ddl_commands()
    LOOP
        -- Enforce that all tables must be prefixed with 'tb_'
        IF obj.object_type = 'table' AND obj.object_identity !~ '^tb_' THEN
            RAISE EXCEPTION 'Table % does not adhere to naming convention: must start with tb_', obj.object_identity;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

CREATE EVENT TRIGGER trg_enforce_table_names
    ON ddl_command_end
    WHEN TAG IN ('CREATE TABLE')
    EXECUTE FUNCTION enforce_naming_conventions();
```

*Edge Case:* Event triggers do not fire for DML statements, and some DDL commands (like `GRANT` or `REVOKE`) are not supported. Always check `pg_event_trigger_ddl_commands()` documentation for support.

---

## Trigger Control and Lifecycle Management

### Conditional Triggers (`WHEN` Clause)

For performance, filter events at the trigger definition level using the `WHEN` clause rather than inside the PL/pgSQL function. This avoids the overhead of setting up the PL/pgSQL execution environment.

```sql
CREATE TRIGGER trg_high_salary_alert
    AFTER UPDATE OF salary ON employees
    FOR EACH ROW
    WHEN (NEW.salary > 100000 AND OLD.salary <= 100000) -- Only fire when crossing the threshold
    EXECUTE FUNCTION notify_high_salary();
```

### Logical Replication and Triggers

By default, triggers **do not fire** on logical replication subscribers. To make a trigger fire for replicated data, you must explicitly enable it for replication:

```sql
-- Enable a trigger for logical replication processes
ALTER TABLE employees ENABLE REPLICA TRIGGER trg_audit_employees;

-- Enable a trigger to always fire (local and replicated)
ALTER TABLE employees ENABLE ALWAYS TRIGGER trg_audit_employees;
```
*Best Practice:* Be extremely cautious with `ALWAYS` triggers in logical replication, as it can lead to duplicate data generation (e.g., auto-updating a timestamp on both master and replica) resulting in replication conflicts.

### Triggers in Partitioned Tables

In PostgreSQL 11+, you can create triggers on a partitioned table, and they automatically cascade to all existing and future partitions. 
- `BEFORE ROW` triggers on the partitioned table cannot change the partition into which a row will be inserted (since partition routing happens before the trigger executes).

### Zero-Downtime Migrations

During a zero-downtime migration (e.g., renaming a column or migrating data formats), triggers are essential to keep the old and new schema elements in sync.
- Create a `BEFORE UPDATE/INSERT` trigger to dual-write data to both the old and new columns.
- Backfill the historical data.
- Drop the old column and the trigger.
- *Caution:* `CREATE TRIGGER` requires an `AccessExclusiveLock` on the table, blocking all reads and writes. To mitigate this in highly concurrent systems, consider executing during low-traffic windows or using alternative sync methods for massive tables.

---
*Previous: 09 - Functions | Next: 11 - JSON & JSONB*
