# 03 - SQL Fundamentals

## What is SQL?

**SQL (Structured Query Language)** is the standard language for managing and manipulating relational databases. It is declarative — you describe *what* you want, and the database engine figures out *how* to get it.

### SQL Categories

| Category | Commands | Purpose |
|----------|----------|---------|
| **DDL** | CREATE, ALTER, DROP, TRUNCATE | Define and modify schema |
| **DML** | SELECT, INSERT, UPDATE, DELETE | Manipulate data |
| **DCL** | GRANT, REVOKE | Control access |
| **TCL** | COMMIT, ROLLBACK, SAVEPOINT | Manage transactions |

---

## Data Types in PostgreSQL

### Numeric Types

| Type | Storage | Range | Precision |
|------|---------|-------|-----------|
| `SMALLINT` | 2 bytes | -32,768 to 32,767 | Exact |
| `INTEGER` | 4 bytes | -2,147,483,648 to 2,147,483,647 | Exact |
| `BIGINT` | 8 bytes | -9,223,372,036,854,775,808 to +... | Exact |
| `DECIMAL(p,s)` | Variable | User-defined | Exact |
| `NUMERIC(p,s)` | Variable | User-defined | Exact |
| `REAL` | 4 bytes | ~6 decimal digits | Approximate |
| `DOUBLE PRECISION` | 8 bytes | ~15 decimal digits | Approximate |
| `SERIAL` | 4 bytes | 1 to 2,147,483,647 | Auto-increment |
| `BIGSERIAL` | 8 bytes | 1 to 9,223,372,036,854,775,807 | Auto-increment |

```sql
CREATE TABLE numeric_examples (
    small_val SMALLINT,
    int_val INTEGER,
    big_val BIGINT,
    exact_val DECIMAL(10, 2),      -- 10 digits total, 2 after decimal
    approx_val DOUBLE PRECISION,
    auto_id SERIAL PRIMARY KEY     -- Auto-incrementing integer
);
```

### Character Types

| Type | Description |
|------|-------------|
| `CHAR(n)` | Fixed-length, padded with spaces |
| `VARCHAR(n)` | Variable-length with max limit |
| `TEXT` | Variable-length unlimited |

```sql
CREATE TABLE text_examples (
    fixed_code CHAR(5),            -- Always 5 characters
    name VARCHAR(100),             -- Up to 100 characters
    description TEXT               -- Unlimited length
);
```

> **Note**: In PostgreSQL, `VARCHAR` and `TEXT` have the same performance. Use `TEXT` unless you specifically need length constraints.

### Date/Time Types

| Type | Description | Example |
|------|-------------|---------|
| `DATE` | Date only | '2024-07-15' |
| `TIME` | Time only | '14:30:00' |
| `TIMESTAMP` | Date and time | '2024-07-15 14:30:00' |
| `TIMESTAMPTZ` | Date, time, timezone | '2024-07-15 14:30:00+00' |
| `INTERVAL` | Time span | '1 year 2 months' |

```sql
CREATE TABLE event_schedule (
    event_date DATE,
    start_time TIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    duration INTERVAL
);
```

### Boolean Type

```sql
CREATE TABLE flags (
    is_enabled BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE
);
-- TRUE, FALSE, NULL (unknown)
-- Aliases: 'yes'/'no', 'on'/'off', '1'/'0', 'true'/'false'
```

### Special PostgreSQL Types

```sql
-- Arrays
CREATE TABLE arrays_example (
    tags TEXT[],
    scores INTEGER[]
);

-- JSON/JSONB
CREATE TABLE json_example (
    data JSON,          -- Stored as text (slower, preserves formatting)
    data_binary JSONB   -- Stored in binary (faster, indexable, recommended)
);

-- UUID
CREATE TABLE uuid_example (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY
);

-- Enumerated Types
CREATE TYPE mood AS ENUM ('happy', 'sad', 'neutral', 'excited');
CREATE TABLE person (
    name TEXT,
    current_mood mood
);

-- Ranges
CREATE TABLE room_reservation (
    room INT,
    during TSRANGE
);
INSERT INTO room_reservation VALUES (1, '[2024-01-01 14:00, 2024-01-01 16:00)');

-- Network Addresses
CREATE TABLE network_info (
    ip_address INET,
    network CIDR,
    mac MACADDR
);

-- Geometric Types
CREATE TABLE locations (
    point POINT,
    box BOX,
    circle CIRCLE,
    polygon POLYGON
);
```

---

## DDL - Data Definition Language

### CREATE TABLE

```sql
-- Basic table
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hire_date DATE NOT NULL DEFAULT CURRENT_DATE,
    salary DECIMAL(10, 2) CHECK (salary > 0),
    department_id INTEGER REFERENCES departments(id),
    is_active BOOLEAN DEFAULT TRUE
);

-- With constraints
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    budget DECIMAL(12, 2),

    -- Table-level constraints
    CONSTRAINT dept_name_unique UNIQUE (name),
    CONSTRAINT positive_budget CHECK (budget >= 0)
);

-- With composite primary key
CREATE TABLE enrollment (
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    grade VARCHAR(2),
    PRIMARY KEY (student_id, course_id)
);
```

### ALTER TABLE

```sql
-- Add a column
ALTER TABLE employees ADD COLUMN phone VARCHAR(20);
ALTER TABLE employees ADD COLUMN age INTEGER CHECK (age >= 18);

-- Drop a column
ALTER TABLE employees DROP COLUMN phone;

-- Rename a column
ALTER TABLE employees RENAME COLUMN first_name TO fname;

-- Change data type
ALTER TABLE employees ALTER COLUMN salary TYPE NUMERIC(12, 2);

-- Add constraint
ALTER TABLE employees ADD CONSTRAINT fk_department 
    FOREIGN KEY (department_id) REFERENCES departments(id);

-- Drop constraint
ALTER TABLE employees DROP CONSTRAINT fk_department;

-- Rename table
ALTER TABLE employees RENAME TO staff;

-- Set default value
ALTER TABLE employees ALTER COLUMN is_active SET DEFAULT TRUE;

-- Remove default
ALTER TABLE employees ALTER COLUMN is_active DROP DEFAULT;

-- Make column NOT NULL
ALTER TABLE employees ALTER COLUMN email SET NOT NULL;

-- Add column with default (populates existing rows)
ALTER TABLE employees ADD COLUMN country VARCHAR(50) DEFAULT 'USA';
```

### DROP TABLE

```sql
-- Drop table (fails if other tables reference it)
DROP TABLE employees;

-- Drop with cascade (removes dependent objects)
DROP TABLE departments CASCADE;

-- Drop if exists
DROP TABLE IF EXISTS temp_table;

-- Drop and recreate
DROP TABLE IF EXISTS employees CASCADE;
CREATE TABLE employees (...);
```

### TRUNCATE TABLE

```sql
-- Remove all rows (faster than DELETE, no triggers fired by default)
TRUNCATE TABLE employees;

-- Truncate multiple tables
TRUNCATE TABLE employees, departments;

-- Truncate with cascade (truncate tables referencing this one)
TRUNCATE TABLE departments CASCADE;

-- Restart identity sequences
TRUNCATE TABLE employees RESTART IDENTITY;
```

---

## DML - Data Manipulation Language

### INSERT

```sql
-- Single row
INSERT INTO employees (first_name, last_name, email, salary, department_id)
VALUES ('Alice', 'Johnson', 'alice@company.com', 75000.00, 1);

-- Multiple rows
INSERT INTO employees (first_name, last_name, email, salary, department_id)
VALUES 
    ('Bob', 'Smith', 'bob@company.com', 65000.00, 2),
    ('Carol', 'Davis', 'carol@company.com', 80000.00, 1),
    ('David', 'Wilson', 'david@company.com', 55000.00, 3);

-- Insert from SELECT
INSERT INTO employees_archive (first_name, last_name, email, hire_date)
SELECT first_name, last_name, email, hire_date
FROM employees
WHERE is_active = FALSE;

-- Insert with RETURNING
INSERT INTO employees (first_name, last_name, email, salary)
VALUES ('Eve', 'Brown', 'eve@company.com', 70000.00)
RETURNING id, created_at;

-- ON CONFLICT (Upsert)
INSERT INTO employees (id, first_name, last_name, email)
VALUES (1, 'Alice', 'Updated', 'alice.new@company.com')
ON CONFLICT (id) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    email = EXCLUDED.email;

-- ON CONFLICT DO NOTHING
INSERT INTO employees (email, first_name, last_name)
VALUES ('alice@company.com', 'Alice', 'Johnson')
ON CONFLICT (email) DO NOTHING;
```

### SELECT

```sql
-- Select all columns
SELECT * FROM employees;

-- Select specific columns
SELECT first_name, last_name, email FROM employees;

-- Select with aliases
SELECT 
    first_name AS fname,
    last_name AS lname,
    salary * 12 AS annual_salary
FROM employees;

-- DISTINCT
SELECT DISTINCT department_id FROM employees;

-- DISTINCT ON (PostgreSQL specific)
SELECT DISTINCT ON (department_id) * FROM employees ORDER BY department_id, salary DESC;

-- LIMIT and OFFSET
SELECT * FROM employees LIMIT 10;
SELECT * FROM employees LIMIT 10 OFFSET 20;  -- Page 3 of 10
SELECT * FROM employees OFFSET 20 LIMIT 10; -- Same as above

-- ORDER BY
SELECT * FROM employees ORDER BY salary DESC;
SELECT * FROM employees ORDER BY last_name ASC, first_name ASC;
SELECT * FROM employees ORDER BY salary DESC NULLS LAST;

-- WHERE clause
SELECT * FROM employees WHERE salary > 60000;
SELECT * FROM employees WHERE department_id = 1 AND salary > 70000;
SELECT * FROM employees WHERE department_id IN (1, 2, 3);
SELECT * FROM employees WHERE salary BETWEEN 50000 AND 70000;
SELECT * FROM employees WHERE last_name LIKE 'S%';      -- Starts with S
SELECT * FROM employees WHERE email LIKE '%@company.com'; -- Ends with @company.com
SELECT * FROM employees WHERE first_name ILIKE 'alice';  -- Case-insensitive
SELECT * FROM employees WHERE phone IS NULL;
SELECT * FROM employees WHERE phone IS NOT NULL;

-- Pattern matching with regular expressions
SELECT * FROM employees WHERE email ~ '^[a-z]+@company\.com$';
SELECT * FROM employees WHERE last_name ~* 'smith|johnson'; -- Case-insensitive
```

### UPDATE

```sql
-- Update single column
UPDATE employees SET salary = salary * 1.05 WHERE department_id = 1;

-- Update multiple columns
UPDATE employees 
SET 
    salary = 80000.00,
    is_active = TRUE
WHERE id = 5;

-- Update from another table
UPDATE employees e
SET salary = s.new_salary
FROM salary_updates s
WHERE e.id = s.employee_id;

-- Update with RETURNING
UPDATE employees SET salary = salary * 1.10 WHERE department_id = 2
RETURNING id, first_name, last_name, salary;
```

### DELETE

```sql
-- Delete specific rows
DELETE FROM employees WHERE is_active = FALSE;

-- Delete all rows (slower than TRUNCATE, fires triggers)
DELETE FROM employees;

-- Delete with RETURNING
DELETE FROM employees WHERE id = 10 RETURNING *;

-- Delete using another table
DELETE FROM employees e
USING departments d
WHERE e.department_id = d.id AND d.name = 'Closed Department';
```

---

## Operators

### Comparison Operators

| Operator | Description |
|----------|-------------|
| `=` | Equal |
| `<>` or `!=` | Not equal |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less than or equal |
| `>=` | Greater than or equal |
| `BETWEEN` | Within a range |
| `IN` | Match any value in a list |
| `NOT IN` | Not match any value in list |
| `LIKE` | Pattern match (%) |
| `ILIKE` | Case-insensitive pattern match |
| `IS NULL` | Is null |
| `IS NOT NULL` | Is not null |
| `~` | Regex match |
| `~*` | Case-insensitive regex match |

### Logical Operators

```sql
SELECT * FROM employees 
WHERE (salary > 70000 OR department_id = 1) 
  AND is_active = TRUE
  AND NOT (hire_date < '2020-01-01');
```

### Mathematical Operators

```sql
SELECT 
    10 + 5 AS addition,
    10 - 5 AS subtraction,
    10 * 5 AS multiplication,
    10 / 3 AS integer_division,    -- 3
    10.0 / 3 AS float_division,    -- 3.333...
    10 % 3 AS modulo,              -- 1
    2 ^ 3 AS exponentiation,       -- 8
    |/ 16 AS square_root,          -- 4
    @ -5 AS absolute_value;        -- 5
```

---

## Functions

### String Functions

```sql
SELECT 
    CONCAT('Hello', ' ', 'World'),           -- 'Hello World'
    'Hello' || ' ' || 'World',               -- 'Hello World'
    LENGTH('Hello'),                          -- 5
    SUBSTRING('Hello World', 1, 5),          -- 'Hello'
    LEFT('Hello World', 5),                   -- 'Hello'
    RIGHT('Hello World', 5),                  -- 'World'
    UPPER('hello'),                           -- 'HELLO'
    LOWER('HELLO'),                           -- 'hello'
    INITCAP('hello world'),                   -- 'Hello World'
    TRIM('  hello  '),                        -- 'hello'
    LTRIM('  hello'),                          -- 'hello'
    RTRIM('hello  '),                          -- 'hello'
    REPLACE('hello world', 'world', 'postgres'), -- 'hello postgres'
    POSITION('lo' IN 'hello'),                 -- 4
    STRPOS('hello', 'lo'),                     -- 4
    SPLIT_PART('a,b,c', ',', 2),              -- 'b'
    REVERSE('hello'),                         -- 'olleh'
    MD5('password'),                          -- hash
    SHA256('password');                       -- hash
```

### Numeric Functions

```sql
SELECT 
    ROUND(3.14159, 2),          -- 3.14
    CEIL(3.2),                   -- 4
    FLOOR(3.8),                  -- 3
    TRUNC(3.14159, 2),           -- 3.14
    ABS(-10),                    -- 10
    SIGN(-10),                   -- -1
    MOD(10, 3),                  -- 1
    POWER(2, 3),                 -- 8
    SQRT(16),                    -- 4
    CBRT(27),                    -- 3
    EXP(1),                      -- 2.718...
    LN(10),                      -- 2.302...
    LOG(100),                    -- 2 (base 10)
    LOG(2, 8),                   -- 3 (base 2)
    RANDOM(),                    -- random 0 to 1
    TRUNC(RANDOM() * 100);      -- random 0 to 99
```

### Date/Time Functions

```sql
SELECT 
    CURRENT_DATE,                -- today's date
    CURRENT_TIME,                -- current time
    CURRENT_TIMESTAMP,           -- date + time
    NOW(),                       -- same as CURRENT_TIMESTAMP
    AGE('1990-05-15'),           -- interval since date
    AGE('2024-01-01', '1990-05-15'), -- interval between dates
    DATE_PART('year', '2024-07-15'::DATE),     -- 2024
    DATE_PART('month', '2024-07-15'::DATE),    -- 7
    DATE_PART('day', '2024-07-15'::DATE),      -- 15
    EXTRACT(YEAR FROM '2024-07-15'::DATE),    -- 2024
    EXTRACT(DOW FROM '2024-07-15'::DATE),      -- day of week (0=Sun)
    TO_CHAR(CURRENT_DATE, 'YYYY-MM-DD'),       -- '2024-07-15'
    TO_DATE('2024-07-15', 'YYYY-MM-DD'),       -- date object
    TO_TIMESTAMP('2024-07-15 14:30:00', 'YYYY-MM-DD HH24:MI:SS'),
    DATE_TRUNC('month', CURRENT_DATE),         -- first of month
    (CURRENT_DATE + INTERVAL '1 month')::DATE, -- add 1 month
    CURRENT_DATE + 7,                           -- add 7 days
    CURRENT_DATE - INTERVAL '1 year';           -- subtract 1 year
```

### Conditional Functions

```sql
SELECT 
    COALESCE(NULL, 'fallback', 'other'),      -- 'fallback'
    NULLIF(10, 10),                            -- NULL
    NULLIF(10, 5),                             -- 10
    GREATEST(1, 5, 3, 9, 2),                   -- 9
    LEAST(1, 5, 3, 9, 2),                      -- 1
    CASE 
        WHEN salary > 100000 THEN 'High'
        WHEN salary > 50000 THEN 'Medium'
        ELSE 'Low'
    END AS salary_category,
    CASE department_id
        WHEN 1 THEN 'Engineering'
        WHEN 2 THEN 'Sales'
        ELSE 'Other'
    END AS department_name;
```

### Aggregate Functions

```sql
SELECT 
    COUNT(*) AS total_rows,
    COUNT(email) AS non_null_emails,
    COUNT(DISTINCT department_id) AS unique_depts,
    SUM(salary) AS total_salary,
    AVG(salary) AS avg_salary,
    MAX(salary) AS highest_salary,
    MIN(salary) AS lowest_salary,
    STRING_AGG(first_name, ', ' ORDER BY first_name) AS names,
    ARRAY_AGG(salary) AS all_salaries,
    JSON_AGG(jsonb_build_object('name', first_name, 'salary', salary)) AS employees_json
FROM employees;
```

---

## GROUP BY and HAVING

```sql
-- Basic grouping
SELECT 
    department_id,
    COUNT(*) AS employee_count,
    AVG(salary) AS avg_salary,
    MAX(salary) AS max_salary
FROM employees
GROUP BY department_id;

-- Group by with multiple columns
SELECT 
    department_id,
    is_active,
    COUNT(*) AS count,
    AVG(salary) AS avg_salary
FROM employees
GROUP BY department_id, is_active;

-- HAVING (filter on aggregates)
SELECT 
    department_id,
    COUNT(*) AS employee_count,
    AVG(salary) AS avg_salary
FROM employees
GROUP BY department_id
HAVING COUNT(*) > 5
   AND AVG(salary) > 60000;

-- GROUP BY with ROLLUP
SELECT 
    COALESCE(department_id::TEXT, 'Total') AS dept,
    COUNT(*) AS count,
    SUM(salary) AS total_salary
FROM employees
GROUP BY ROLLUP(department_id);

-- GROUP BY with CUBE
SELECT 
    department_id,
    is_active,
    COUNT(*) AS count
FROM employees
GROUP BY CUBE(department_id, is_active);
```

---

## Summary

You now understand:
- All PostgreSQL data types and when to use them
- DDL commands: CREATE, ALTER, DROP, TRUNCATE
- DML commands: INSERT, SELECT, UPDATE, DELETE
- Comparison, logical, and mathematical operators
- Essential string, numeric, date/time, conditional, and aggregate functions
- GROUP BY, HAVING, and advanced grouping

---
*Previous: [02 - Installation & Setup](02-installation-setup.md) | Next: [04 - Joins & Relationships](04-joins-relationships.md)*
