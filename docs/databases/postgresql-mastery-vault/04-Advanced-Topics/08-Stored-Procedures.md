---
tags: [postgresql, advanced, stored-procedures, functions, triggers]
---

# Stored Procedures and Functions

PostgreSQL supports server-side functions and procedures in multiple languages.

## Functions (Return Values)

```sql
-- Simple function
CREATE OR REPLACE FUNCTION get_user_count()
RETURNS INTEGER LANGUAGE sql AS $$
    SELECT COUNT(*) FROM users;
$$;

SELECT get_user_count();

-- Function with parameters
CREATE OR REPLACE FUNCTION total_orders(p_customer_id BIGINT)
RETURNS NUMERIC LANGUAGE plpgsql AS $$
DECLARE
    total NUMERIC;
BEGIN
    SELECT COALESCE(SUM(amount), 0) INTO total
    FROM orders WHERE customer_id = p_customer_id;
    RETURN total;
END;
$$;

SELECT total_orders(42);
```

## Set-Returning Functions

```sql
-- Return multiple rows
CREATE OR REPLACE FUNCTION top_customers(n INTEGER DEFAULT 10)
RETURNS TABLE(id BIGINT, name TEXT, total NUMERIC) LANGUAGE sql AS $$
    SELECT c.id, c.name, SUM(o.amount) AS total
    FROM customers c
    JOIN orders o ON o.customer_id = c.id
    GROUP BY c.id, c.name
    ORDER BY total DESC
    LIMIT n;
$$;

SELECT * FROM top_customers(5);
```

## Procedures (PostgreSQL 11+)

Procedures can control transactions (COMMIT/ROLLBACK) inside them — functions cannot.

```sql
CREATE OR REPLACE PROCEDURE archive_old_orders(days_old INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO orders_archive
        SELECT * FROM orders WHERE created_at < NOW() - (days_old || ' days')::INTERVAL;

    DELETE FROM orders WHERE created_at < NOW() - (days_old || ' days')::INTERVAL;

    COMMIT;  -- allowed inside PROCEDURE, not FUNCTION
END;
$$;

CALL archive_old_orders(365);
```

## Triggers

```sql
-- Auto-update updated_at column
CREATE OR REPLACE FUNCTION touch_updated_at()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_touch_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

-- Audit log trigger
CREATE OR REPLACE FUNCTION audit_log()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO audit_log(table_name, operation, row_data, changed_by, changed_at)
    VALUES (TG_TABLE_NAME, TG_OP, row_to_json(NEW), current_user, NOW());
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_audit_users
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION audit_log();
```

## Trigger Variables

| Variable | Description |
|----------|-------------|
| `NEW` | New row (INSERT/UPDATE) |
| `OLD` | Old row (UPDATE/DELETE) |
| `TG_OP` | Operation: 'INSERT', 'UPDATE', 'DELETE', 'TRUNCATE' |
| `TG_TABLE_NAME` | Table name |
| `TG_WHEN` | 'BEFORE' or 'AFTER' |

## Practice

```sql
-- Create a function and use it
CREATE OR REPLACE FUNCTION is_high_earner(emp_salary NUMERIC)
RETURNS BOOLEAN LANGUAGE sql AS $$
    SELECT emp_salary > (SELECT AVG(salary) FROM employees);
$$;

SELECT name, salary, is_high_earner(salary) FROM employees;
```

## Next

- [[05-Administration/01-Users-Roles-Permissions|Users and Roles]]
- [[06-Extensions/01-PostGIS|PostGIS]]
