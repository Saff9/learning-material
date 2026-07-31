# 09 - Functions & Procedures

> SQL functions, PL/pgSQL, control flow, cursors, dynamic SQL, and custom aggregates.

---

## SQL Functions

```sql
-- Simple function
CREATE OR REPLACE FUNCTION get_employee_name(emp_id BIGINT)
RETURNS VARCHAR AS $$
    SELECT first_name || ' ' || last_name FROM employees WHERE id = emp_id;
$$ LANGUAGE SQL;

-- Function returning table
CREATE OR REPLACE FUNCTION get_employees_by_dept(dept_id INTEGER)
RETURNS TABLE (emp_id BIGINT, full_name VARCHAR, emp_salary NUMERIC) AS $$
    SELECT id, first_name || ' ' || last_name, salary
    FROM employees WHERE department_id = dept_id;
$$ LANGUAGE SQL;

-- Multiple parameters
CREATE OR REPLACE FUNCTION calculate_bonus(salary NUMERIC, rating INTEGER)
RETURNS NUMERIC AS $$
    SELECT salary * (0.05 + (rating * 0.01));
$$ LANGUAGE SQL;
```

---

## PL/pgSQL Functions

```sql
CREATE OR REPLACE FUNCTION transfer_employee(
    emp_id BIGINT, new_dept_id INTEGER
) RETURNS TEXT AS $$
DECLARE
    old_dept_name VARCHAR;
    new_dept_name VARCHAR;
    emp_name VARCHAR;
BEGIN
    SELECT first_name || ' ' || last_name INTO emp_name
    FROM employees WHERE id = emp_id;

    SELECT d.name INTO old_dept_name
    FROM employees e JOIN departments d ON e.department_id = d.id
    WHERE e.id = emp_id;

    SELECT name INTO new_dept_name FROM departments WHERE id = new_dept_id;

    UPDATE employees SET department_id = new_dept_id WHERE id = emp_id;

    RETURN emp_name || ' transferred from ' || old_dept_name || ' to ' || new_dept_name;
END;
$$ LANGUAGE plpgsql;

-- Exception handling
CREATE OR REPLACE FUNCTION safe_divide(a NUMERIC, b NUMERIC)
RETURNS NUMERIC AS $$
BEGIN
    IF b = 0 THEN
        RAISE EXCEPTION 'Division by zero';
    END IF;
    RETURN a / b;
EXCEPTION
    WHEN division_by_zero THEN RETURN NULL;
    WHEN OTHERS THEN RAISE NOTICE 'Error: %', SQLERRM; RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

---

## Control Flow

```sql
CREATE OR REPLACE FUNCTION employee_report()
RETURNS TABLE (dept_name VARCHAR, emp_count BIGINT, total_salary NUMERIC, status TEXT) AS $$
DECLARE
    total_budget NUMERIC := 5000000;
BEGIN
    FOR dept_name, emp_count, total_salary IN
        SELECT d.name, COUNT(e.id), COALESCE(SUM(e.salary), 0)
        FROM departments d LEFT JOIN employees e ON d.id = e.department_id
        GROUP BY d.id, d.name ORDER BY d.name
    LOOP
        IF total_salary > total_budget * 0.3 THEN status := 'OVER BUDGET';
        ELSIF total_salary > total_budget * 0.2 THEN status := 'HIGH';
        ELSIF total_salary > total_budget * 0.1 THEN status := 'MODERATE';
        ELSE status := 'LOW';
        END IF;
        RETURN NEXT;
    END LOOP;
    RETURN;
END;
$$ LANGUAGE plpgsql;
```

---

## RETURN NEXT vs RETURN QUERY

```sql
-- RETURN NEXT: Build result row by row
CREATE FUNCTION get_paged(page_size INT, page_num INT)
RETURNS TABLE (id INT, name TEXT) AS $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT e.id, e.first_name FROM employees e
             ORDER BY e.id LIMIT page_size OFFSET (page_num - 1) * page_size
    LOOP
        id := r.id; name := r.name; RETURN NEXT;
    END LOOP;
    RETURN;
END;
$$ LANGUAGE plpgsql;

-- RETURN QUERY: Direct query return
CREATE FUNCTION get_high_earners(min_salary NUMERIC)
RETURNS TABLE (id INT, name TEXT, salary NUMERIC) AS $$
BEGIN
    RETURN QUERY
    SELECT e.id, e.first_name || ' ' || e.last_name, e.salary
    FROM employees e WHERE e.salary >= min_salary ORDER BY e.salary DESC;
END;
$$ LANGUAGE plpgsql;
```

---

## Dynamic SQL

```sql
CREATE OR REPLACE FUNCTION get_table_count(table_name TEXT)
RETURNS BIGINT AS $$
DECLARE result BIGINT;
BEGIN
    EXECUTE format('SELECT COUNT(*) FROM %I', table_name) INTO result;
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- With parameters
CREATE OR REPLACE FUNCTION search_employees(search_term TEXT)
RETURNS TABLE (id INT, name TEXT) AS $$
BEGIN
    RETURN QUERY EXECUTE
        'SELECT id, first_name || '' '' || last_name FROM employees 
         WHERE first_name ILIKE $1 OR last_name ILIKE $1'
    USING '%' || search_term || '%';
END;
$$ LANGUAGE plpgsql;
```

---

## Custom Aggregates

```sql
-- Product aggregate
CREATE OR REPLACE FUNCTION multiply_accumulate(state NUMERIC, val NUMERIC)
RETURNS NUMERIC AS $$ SELECT state * val; $$ LANGUAGE SQL IMMUTABLE;

CREATE AGGREGATE product (NUMERIC) (
    SFUNC = multiply_accumulate,
    STYPE = NUMERIC,
    INITCOND = '1'
);

SELECT product(salary) FROM employees;
```

---
*Previous: 08 - Transactions | Next: 10 - Triggers & Event Triggers*
