# 09 - Functions & Procedures

> Comprehensive guide to SQL functions, PL/pgSQL, Procedures, control flow, cursors, dynamic SQL, custom aggregates, and advanced execution mechanics.

---

## SQL Functions vs PL/pgSQL vs Procedures

PostgreSQL provides multiple ways to encapsulate logic. 
- **SQL Functions**: Best for simple queries. They are parsed and planned inline by the query optimizer, often leading to better performance for simple operations.
- **PL/pgSQL Functions**: Procedural language supporting variables, loops, exception handling, and complex conditional logic.
- **Procedures**: Introduced in PG 11, procedures can manage transactions (`COMMIT`/`ROLLBACK` internally), which functions cannot.

### SQL Functions

```sql
-- Simple function with STRICT and IMMUTABLE for optimization
CREATE OR REPLACE FUNCTION get_employee_name(emp_id BIGINT)
RETURNS VARCHAR AS $$
    SELECT first_name || ' ' || last_name FROM employees WHERE id = emp_id;
$$ LANGUAGE SQL STABLE STRICT PARALLEL SAFE;

-- Function returning table (Set Returning Function - SRF)
CREATE OR REPLACE FUNCTION get_employees_by_dept(dept_id INTEGER)
RETURNS TABLE (emp_id BIGINT, full_name VARCHAR, emp_salary NUMERIC) AS $$
    SELECT id, first_name || ' ' || last_name, salary
    FROM employees WHERE department_id = dept_id;
$$ LANGUAGE SQL STABLE;
```

*Architectural Detail*: When using `LANGUAGE SQL`, the planner can "inline" the function directly into the calling query tree, allowing global optimizations. `STRICT` prevents the function from firing if any argument is NULL, returning NULL immediately.

---

## PL/pgSQL Functions & Control Flow

PL/pgSQL is a block-structured language. It caches query plans per session, which can be highly performant but might cause issues with heavily skewed data (plan invalidation).

```sql
CREATE OR REPLACE FUNCTION transfer_employee(
    emp_id BIGINT, new_dept_id INTEGER
) RETURNS TEXT AS $$
DECLARE
    old_dept_name VARCHAR;
    new_dept_name VARCHAR;
    emp_name VARCHAR;
BEGIN
    -- INTO strictly expects one row; use STRICT keyword in INTO to raise an error if not exactly 1 row
    SELECT first_name || ' ' || last_name INTO STRICT emp_name
    FROM employees WHERE id = emp_id;

    SELECT d.name INTO old_dept_name
    FROM employees e JOIN departments d ON e.department_id = d.id
    WHERE e.id = emp_id;

    SELECT name INTO new_dept_name FROM departments WHERE id = new_dept_id;

    UPDATE employees SET department_id = new_dept_id WHERE id = emp_id;

    RETURN emp_name || ' transferred from ' || old_dept_name || ' to ' || new_dept_name;
EXCEPTION
    WHEN no_data_found THEN
        RAISE EXCEPTION 'Employee or Department not found';
    WHEN too_many_rows THEN
        RAISE EXCEPTION 'Data anomaly: Multiple records found';
END;
$$ LANGUAGE plpgsql;
```

---

## Procedures (Transaction Control)

Unlike functions, procedures allow you to commit or rollback transactions mid-execution, which is vital for heavy batch processing to prevent massive lock accumulation and bloat.

```sql
CREATE OR REPLACE PROCEDURE bulk_salary_update(batch_size INT)
LANGUAGE plpgsql
AS $$
DECLARE
    processed INT := 0;
BEGIN
    LOOP
        UPDATE employees SET salary = salary * 1.05 
        WHERE id IN (
            SELECT id FROM employees WHERE needs_update = TRUE LIMIT batch_size
        );
        
        EXIT WHEN NOT FOUND;
        
        COMMIT; -- Commit the batch to free locks and resources
        processed := processed + batch_size;
        RAISE NOTICE 'Processed % records', processed;
    END LOOP;
END;
$$;

-- Execution
CALL bulk_salary_update(1000);
```

---

## Function Attributes & Performance Tuning

Marking functions correctly is critical for query planner efficiency, parallel execution, and index usage (e.g., using functions in `CREATE INDEX`).

- **VOLATILE** (Default): Can modify the database or return different results for the same arguments (e.g., `random()`, `now()`). Evaluated every row.
- **STABLE**: Cannot modify the database. Guaranteed to return the same results given the same arguments *within a single statement scan*. Evaluated once per query.
- **IMMUTABLE**: Cannot modify the database. Guaranteed to return the same results given the same arguments *forever*. Can be heavily cached and used in functional indexes.
- **PARALLEL {SAFE | RESTRICTED | UNSAFE}**: Determines if the function can be pushed to parallel worker processes.
- **COST & ROWS**: Hints for the query planner. High cost discourages execution until filters reduce the row count.

---

## Security: DEFINER vs INVOKER & RBAC

By default, functions run as `SECURITY INVOKER` (executing with the permissions of the calling user). 

`SECURITY DEFINER` runs the function with the privileges of the user who *created* it. This is useful for exposing specific elevated tasks (like a restricted `UPDATE`) without granting direct table access.

> **Security Edge Case (Search Path Attack)**: A malicious user might create an object with a conflicting name in their schema. Always force a safe `search_path` on `SECURITY DEFINER` functions.

```sql
CREATE OR REPLACE FUNCTION reset_password(user_id INT, new_pwd TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER          -- Run as creator (e.g., admin)
SET search_path = public, pg_temp -- Prevent search_path hijacking
AS $$
BEGIN
    UPDATE app_users SET password_hash = crypt(new_pwd, gen_salt('bf')) WHERE id = user_id;
    RETURN FOUND;
END;
$$;
```

---

## RETURN NEXT vs RETURN QUERY

```sql
-- RETURN NEXT: Build result row by row (Higher memory overhead in PL/pgSQL)
CREATE FUNCTION get_paged(page_size INT, page_num INT)
RETURNS TABLE (id INT, name TEXT) AS $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT e.id, e.first_name FROM employees e
             ORDER BY e.id LIMIT page_size OFFSET (page_num - 1) * page_size
    LOOP
        id := r.id; name := r.name; 
        RETURN NEXT; -- Caches rows in memory before returning
    END LOOP;
    RETURN;
END;
$$ LANGUAGE plpgsql;

-- RETURN QUERY: Direct query return (More efficient, acts like a pass-through)
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

## Dynamic SQL & SQL Injection Prevention

When table names or column names must be parameterized, use `EXECUTE` with `format()` to securely build queries. Never concatenate raw strings!

- `%I`: Identifiers (tables, columns). Safely quotes them.
- `%L`: Literals (values). Safely quotes them.

```sql
CREATE OR REPLACE FUNCTION get_dynamic_aggregate(
    table_name TEXT, col_name TEXT, agg_func TEXT
) RETURNS NUMERIC AS $$
DECLARE 
    result NUMERIC;
BEGIN
    -- Validate agg_func against a whitelist to prevent injection
    IF agg_func NOT IN ('SUM', 'AVG', 'MIN', 'MAX') THEN
        RAISE EXCEPTION 'Invalid aggregate function';
    END IF;

    -- Securely format the dynamic query
    EXECUTE format('SELECT %s(%I) FROM %I', agg_func, col_name, table_name) 
    INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;
```
For dynamic values, always use `USING` rather than string interpolation:

```sql
EXECUTE 'SELECT * FROM users WHERE username = $1' USING user_input;
```

---

## Advanced Feature: Cursors

Cursors are useful when processing massive datasets that do not fit into memory. Instead of executing the query at once, cursors fetch a few rows at a time.

```sql
CREATE OR REPLACE FUNCTION process_large_dataset() 
RETURNS VOID AS $$
DECLARE
    emp_cursor CURSOR FOR SELECT id, salary FROM employees WHERE status = 'ACTIVE';
    emp_record RECORD;
BEGIN
    OPEN emp_cursor;
    LOOP
        -- Fetch next batch
        FETCH NEXT FROM emp_cursor INTO emp_record;
        EXIT WHEN NOT FOUND;
        
        -- Process heavy logic here
    END LOOP;
    CLOSE emp_cursor;
END;
$$ LANGUAGE plpgsql;
```

---

## Custom Aggregates

Custom aggregates combine a state transition function (`SFUNC`) and an optional final function (`FINALFUNC`). 

```sql
-- State transition function
CREATE OR REPLACE FUNCTION multiply_accumulate(state NUMERIC, val NUMERIC)
RETURNS NUMERIC AS $$ 
    SELECT COALESCE(state, 1) * COALESCE(val, 1); 
$$ LANGUAGE SQL IMMUTABLE PARALLEL SAFE;

-- Aggregate definition
CREATE AGGREGATE product (NUMERIC) (
    SFUNC = multiply_accumulate,
    STYPE = NUMERIC,
    INITCOND = '1',
    PARALLEL = SAFE
);

SELECT department_id, product(growth_multiplier) FROM department_metrics GROUP BY department_id;
```

---

## Multi-Language Extensions (PL/Python & PL/Rust)

PostgreSQL natively supports extending procedural capabilities into other languages.
> **Note on Cloud Limits**: Managed services (AWS RDS, GCP Cloud SQL) restrict "untrusted" languages (like `plpython3u`) because they interact directly with the OS filesystem. Safe, trusted variants like PL/v8 (JavaScript) or PL/Rust (compiled for safety and performance) are heavily favored in modern cloud stacks.

### PL/Python (Machine Learning / Data Science)
*(Requires superuser and `CREATE EXTENSION plpython3u`)*
```sql
CREATE OR REPLACE FUNCTION analyze_sentiment(review_text TEXT)
RETURNS FLOAT AS $$
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(review_text)['compound']
$$ LANGUAGE plpython3u;
```

### PL/Rust (High Performance & Safe)
PL/Rust brings memory safety and bare-metal performance to PG functions.
```sql
CREATE OR REPLACE FUNCTION fast_levenshtein(a TEXT, b TEXT)
RETURNS INT LANGUAGE plrust AS $$
    // Rust crate logic for extremely fast distance calculation
    Ok(strsim::levenshtein(a.expect(""), b.expect("")).try_into().unwrap())
$$;
```

---
*Previous: 08 - Transactions | Next: 10 - Triggers & Event Triggers*
