# 08 - Functions & Triggers

## Functions

PostgreSQL supports functions in multiple languages. Functions encapsulate reusable logic.

### SQL Functions

```sql
-- Simple function
CREATE OR REPLACE FUNCTION get_employee_name(emp_id INTEGER)
RETURNS VARCHAR AS $$
    SELECT first_name || ' ' || last_name 
    FROM employees 
    WHERE id = emp_id;
$$ LANGUAGE SQL;

-- Usage
SELECT get_employee_name(1);

-- Function with multiple parameters
CREATE OR REPLACE FUNCTION calculate_bonus(
    salary DECIMAL,
    performance_rating INTEGER
)
RETURNS DECIMAL AS $$
    SELECT salary * (0.05 + (performance_rating * 0.01));
$$ LANGUAGE SQL;

-- Function returning a table
CREATE OR REPLACE FUNCTION get_employees_by_dept(dept_id INTEGER)
RETURNS TABLE (
    emp_id INTEGER,
    full_name VARCHAR,
    emp_salary DECIMAL
) AS $$
    SELECT 
        id,
        first_name || ' ' || last_name,
        salary
    FROM employees
    WHERE department_id = dept_id;
$$ LANGUAGE SQL;

-- Usage
SELECT * FROM get_employees_by_dept(1);
```

### PL/pgSQL Functions

PL/pgSQL is PostgreSQL's procedural language. More powerful than SQL functions.

```sql
-- Basic PL/pgSQL function
CREATE OR REPLACE FUNCTION get_employee_count(dept_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
    count_result INTEGER;
BEGIN
    SELECT COUNT(*) INTO count_result
    FROM employees
    WHERE department_id = dept_id;

    RETURN count_result;
END;
$$ LANGUAGE plpgsql;

-- Function with multiple statements
CREATE OR REPLACE FUNCTION transfer_employee(
    emp_id INTEGER,
    new_dept_id INTEGER
)
RETURNS TEXT AS $$
DECLARE
    old_dept_name VARCHAR;
    new_dept_name VARCHAR;
    emp_name VARCHAR;
BEGIN
    -- Get employee info
    SELECT first_name || ' ' || last_name INTO emp_name
    FROM employees WHERE id = emp_id;

    -- Get old department
    SELECT d.name INTO old_dept_name
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    WHERE e.id = emp_id;

    -- Get new department
    SELECT name INTO new_dept_name
    FROM departments WHERE id = new_dept_id;

    -- Update employee
    UPDATE employees 
    SET department_id = new_dept_id 
    WHERE id = emp_id;

    RETURN emp_name || ' transferred from ' || old_dept_name || ' to ' || new_dept_name;
END;
$$ LANGUAGE plpgsql;

-- Function with exception handling
CREATE OR REPLACE FUNCTION safe_divide(a NUMERIC, b NUMERIC)
RETURNS NUMERIC AS $$
BEGIN
    IF b = 0 THEN
        RAISE EXCEPTION 'Division by zero is not allowed';
    END IF;
    RETURN a / b;
EXCEPTION
    WHEN division_by_zero THEN
        RAISE NOTICE 'Caught division by zero';
        RETURN NULL;
    WHEN OTHERS THEN
        RAISE NOTICE 'Unexpected error: %', SQLERRM;
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

### Variable Types and Control Flow

```sql
CREATE OR REPLACE FUNCTION employee_report()
RETURNS TABLE (
    dept_name VARCHAR,
    emp_count BIGINT,
    total_salary NUMERIC,
    avg_salary NUMERIC,
    status TEXT
) AS $$
DECLARE
    total_budget NUMERIC := 5000000;  -- Variable with default
    current_total NUMERIC;
BEGIN
    FOR dept_name, emp_count, total_salary, avg_salary IN
        SELECT 
            d.name,
            COUNT(e.id),
            COALESCE(SUM(e.salary), 0),
            COALESCE(AVG(e.salary), 0)
        FROM departments d
        LEFT JOIN employees e ON d.id = e.department_id
        GROUP BY d.id, d.name
        ORDER BY d.name
    LOOP
        -- Determine status
        IF total_salary > total_budget * 0.3 THEN
            status := 'OVER BUDGET';
        ELSIF total_salary > total_budget * 0.2 THEN
            status := 'HIGH';
        ELSIF total_salary > total_budget * 0.1 THEN
            status := 'MODERATE';
        ELSE
            status := 'LOW';
        END IF;

        RETURN NEXT;
    END LOOP;

    RETURN;
END;
$$ LANGUAGE plpgsql;
```

### RETURN NEXT vs RETURN QUERY

```sql
-- RETURN NEXT: Build result set row by row
CREATE OR REPLACE FUNCTION get_employees_paged(
    page_size INTEGER,
    page_num INTEGER
)
RETURNS TABLE (id INTEGER, name VARCHAR, salary NUMERIC) AS $$
DECLARE
    emp_record RECORD;
    offset_val INTEGER := (page_num - 1) * page_size;
    counter INTEGER := 0;
BEGIN
    FOR emp_record IN 
        SELECT e.id, e.first_name || ' ' || e.last_name, e.salary
        FROM employees e
        ORDER BY e.id
        LIMIT page_size OFFSET offset_val
    LOOP
        id := emp_record.id;
        name := emp_record.name;
        salary := emp_record.salary;
        RETURN NEXT;
    END LOOP;
    RETURN;
END;
$$ LANGUAGE plpgsql;

-- RETURN QUERY: Return result of a query directly
CREATE OR REPLACE FUNCTION get_high_earners(min_salary NUMERIC)
RETURNS TABLE (id INTEGER, name VARCHAR, salary NUMERIC) AS $$
BEGIN
    RETURN QUERY
    SELECT e.id, e.first_name || ' ' || e.last_name, e.salary
    FROM employees e
    WHERE e.salary >= min_salary
    ORDER BY e.salary DESC;
END;
$$ LANGUAGE plpgsql;
```

### Dynamic SQL

```sql
-- Execute dynamic SQL
CREATE OR REPLACE FUNCTION get_table_count(table_name TEXT)
RETURNS BIGINT AS $$
DECLARE
    result BIGINT;
BEGIN
    EXECUTE format('SELECT COUNT(*) FROM %I', table_name) INTO result;
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Dynamic SQL with parameters
CREATE OR REPLACE FUNCTION search_employees(search_term TEXT)
RETURNS TABLE (id INTEGER, name TEXT) AS $$
BEGIN
    RETURN QUERY EXECUTE 
        'SELECT id, first_name || '' '' || last_name 
         FROM employees 
         WHERE first_name ILIKE $1 OR last_name ILIKE $1'
    USING '%' || search_term || '%';
END;
$$ LANGUAGE plpgsql;
```

### Function Volatility

```sql
-- IMMUTABLE: Same inputs always give same output, no DB access
CREATE OR REPLACE FUNCTION add_numbers(a INTEGER, b INTEGER)
RETURNS INTEGER AS $$
    SELECT a + b;
$$ LANGUAGE SQL IMMUTABLE;

-- STABLE: Same output within a single query, no DB modifications
CREATE OR REPLACE FUNCTION get_current_dept(emp_id INTEGER)
RETURNS VARCHAR AS $$
    SELECT d.name 
    FROM employees e 
    JOIN departments d ON e.department_id = d.id 
    WHERE e.id = emp_id;
$$ LANGUAGE SQL STABLE;

-- VOLATILE (default): May modify DB, output can change
CREATE OR REPLACE FUNCTION update_last_login(user_id INTEGER)
RETURNS VOID AS $$
    UPDATE users SET last_login = NOW() WHERE id = user_id;
$$ LANGUAGE SQL VOLATILE;
```

---

## Triggers

Triggers execute automatically when specified events occur.

### Trigger Functions

```sql
-- Trigger function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger
CREATE TRIGGER trg_employees_updated_at
    BEFORE UPDATE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

### Trigger Types

```sql
-- BEFORE INSERT: Modify data before insertion
CREATE OR REPLACE FUNCTION set_created_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.created_at = CURRENT_TIMESTAMP;
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_employees_created
    BEFORE INSERT ON employees
    FOR EACH ROW
    EXECUTE FUNCTION set_created_at();

-- AFTER INSERT: Log the insertion
CREATE OR REPLACE FUNCTION log_employee_insert()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (table_name, action, record_id, new_data, changed_at)
    VALUES ('employees', 'INSERT', NEW.id, row_to_json(NEW), NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_log_employee_insert
    AFTER INSERT ON employees
    FOR EACH ROW
    EXECUTE FUNCTION log_employee_insert();

-- BEFORE DELETE: Prevent deletion or archive
CREATE OR REPLACE FUNCTION archive_employee()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO employees_archive (id, first_name, last_name, email, 
                                   salary, hire_date, deleted_at)
    VALUES (OLD.id, OLD.first_name, OLD.last_name, OLD.email,
            OLD.salary, OLD.hire_date, NOW());
    RETURN OLD;  -- Allow deletion to proceed
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_archive_employee
    BEFORE DELETE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION archive_employee();

-- INSTEAD OF: For views
CREATE OR REPLACE FUNCTION insert_into_employee_view()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO employees (first_name, last_name, email, salary, department_id)
    VALUES (NEW.first_name, NEW.last_name, NEW.email, NEW.salary, NEW.department_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_insert_employee_view
    INSTEAD OF INSERT ON employee_department_view
    FOR EACH ROW
    EXECUTE FUNCTION insert_into_employee_view();
```

### Trigger Variables

```sql
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- NEW contains the new row
        RAISE NOTICE 'Inserting: %', NEW;
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        -- OLD contains old values, NEW contains new values
        RAISE NOTICE 'Updating id=%: % -> %', OLD.id, OLD, NEW;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        -- OLD contains the deleted row
        RAISE NOTICE 'Deleting: %', OLD;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- TG_NAME: trigger name
-- TG_WHEN: BEFORE, AFTER, INSTEAD OF
-- TG_LEVEL: ROW or STATEMENT
-- TG_OP: INSERT, UPDATE, DELETE, TRUNCATE
-- TG_RELID: OID of table
-- TG_RELNAME: table name
-- TG_TABLE_NAME: table name
-- TG_TABLE_SCHEMA: schema name
-- TG_NARGS: number of arguments
-- TG_ARGV[]: trigger arguments
```

### Statement-Level Triggers

```sql
-- Run once per statement, not per row
CREATE OR REPLACE FUNCTION notify_data_change()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('table_changes', 
        json_build_object(
            'table', TG_TABLE_NAME,
            'operation', TG_OP,
            'time', NOW()
        )::TEXT
    );
    RETURN NULL;  -- Ignored for statement triggers
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_notify_changes
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH STATEMENT
    EXECUTE FUNCTION notify_data_change();
```

### Conditional Triggers

```sql
-- Only fire when condition is met
CREATE TRIGGER trg_high_salary_alert
    AFTER INSERT OR UPDATE OF salary ON employees
    FOR EACH ROW
    WHEN (NEW.salary > 100000)
    EXECUTE FUNCTION notify_high_salary();
```

### Disabling and Enabling Triggers

```sql
-- Disable a trigger
ALTER TABLE employees DISABLE TRIGGER trg_employees_updated_at;

-- Disable all triggers
ALTER TABLE employees DISABLE TRIGGER ALL;

-- Enable a trigger
ALTER TABLE employees ENABLE TRIGGER trg_employees_updated_at;

-- Enable all triggers
ALTER TABLE employees ENABLE TRIGGER ALL;
```

---

## Event Triggers

React to DDL events (CREATE, ALTER, DROP).

```sql
-- Log all table creations
CREATE OR REPLACE FUNCTION log_ddl()
RETURNS EVENT_TRIGGER AS $$
BEGIN
    INSERT INTO ddl_log (event_type, object_type, object_name, command, executed_at)
    SELECT 
        TG_EVENT,
        TG_OBJECT_TYPE,
        TG_OBJECT_IDENTITY,
        TG_TAG,
        NOW();
END;
$$ LANGUAGE plpgsql;

CREATE EVENT TRIGGER trg_log_ddl
    ON ddl_command_end
    EXECUTE FUNCTION log_ddl();

-- Specific events only
CREATE EVENT TRIGGER trg_log_table_changes
    ON ddl_command_end
    WHEN TAG IN ('CREATE TABLE', 'ALTER TABLE', 'DROP TABLE')
    EXECUTE FUNCTION log_ddl();

-- Disable event trigger
ALTER EVENT TRIGGER trg_log_ddl DISABLE;

-- Drop event trigger
DROP EVENT TRIGGER trg_log_ddl;
```

---

## Custom Aggregates

```sql
-- Create a custom aggregate
CREATE OR REPLACE FUNCTION array_accumulate(state ANYARRAY, val ANYELEMENT)
RETURNS ANYARRAY AS $$
    SELECT array_append(state, val);
$$ LANGUAGE SQL IMMUTABLE;

CREATE AGGREGATE array_accumulate (ANYELEMENT)
(
    SFUNC = array_accumulate,
    STYPE = ANYARRAY,
    INITCOND = '{}'
);

-- Usage
SELECT department_id, array_accumulate(first_name) 
FROM employees 
GROUP BY department_id;

-- Product aggregate (multiply all values)
CREATE OR REPLACE FUNCTION multiply_accumulate(state NUMERIC, val NUMERIC)
RETURNS NUMERIC AS $$
    SELECT state * val;
$$ LANGUAGE SQL IMMUTABLE;

CREATE AGGREGATE product (NUMERIC)
(
    SFUNC = multiply_accumulate,
    STYPE = NUMERIC,
    INITCOND = '1'
);

SELECT product(salary) FROM employees;
```

---

## Summary

| Feature | Use Case |
|---------|----------|
| **SQL Functions** | Simple, single-statement logic |
| **PL/pgSQL Functions** | Complex logic, loops, exceptions |
| **BEFORE Triggers** | Validate/modify data before change |
| **AFTER Triggers** | Log, notify, cascade changes |
| **INSTEAD OF Triggers** | Make views writable |
| **Event Triggers** | React to DDL changes |
| **Custom Aggregates** | Specialized aggregation logic |

---
*Previous: [07 - Transactions & ACID](07-transactions-acid.md) | Next: [09 - JSON & JSONB](09-json-jsonb.md)*
