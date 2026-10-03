# 03 - SQL Fundamentals & Advanced Architectures

> Complete coverage of PostgreSQL data types, DDL, DML, operators, functions, and advanced concepts including Partitioning, Vector Search, Security, and Replication.

---

## Data Types

### Numeric

| Type | Size | Range | Use Case |
|------|------|-------|----------|
| SMALLINT | 2 bytes | -32768 to 32767 | Counters, flags |
| INTEGER | 4 bytes | -2B to 2B | Primary keys, counts |
| BIGINT | 8 bytes | -9E18 to 9E18 | Large IDs, timestamps |
| NUMERIC(p,s) | variable | exact | Money, precise calculations |
| REAL | 4 bytes | ~6 digits | Scientific, approximations |
| DOUBLE PRECISION | 8 bytes | ~15 digits | Float calculations |
| SERIAL | 4 bytes | auto 1-2B | Auto-increment PK |
| BIGSERIAL | 8 bytes | auto 1-9E18 | Large auto-increment |
| GENERATED ALWAYS AS IDENTITY | 4-8 bytes | auto | SQL standard replacement for SERIAL |

```sql
-- Modern identity columns (preferred over SERIAL)
CREATE TABLE products (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    price NUMERIC(19, 4) NOT NULL,  -- Never use FLOAT for money
    quantity INTEGER CHECK (quantity >= 0)
);

-- Small lookup table
CREATE TABLE status_codes (
    code SMALLINT PRIMARY KEY,
    label VARCHAR(50)
);
```

### Character Types

| Type | Description | When to Use |
|------|-------------|-------------|
| CHAR(n) | Fixed width, space-padded | Codes, fixed IDs |
| VARCHAR(n) | Variable, max n | Names, titles, emails |
| TEXT | Unlimited | Descriptions, content, JSON |

> PostgreSQL stores VARCHAR and TEXT identically. Use TEXT unless you need a length constraint.

```sql
CREATE TABLE articles (
    slug CHAR(8) PRIMARY KEY,           -- Fixed length
    title VARCHAR(200) NOT NULL,        -- Reasonable limit
    body TEXT NOT NULL,                  -- Unlimited
    excerpt VARCHAR(500)                 -- Could also be TEXT
);
```

### Date/Time Types

| Type | Stores | Example |
|------|--------|---------|
| DATE | Date only | '2026-07-15' |
| TIME | Time only | '14:30:00' |
| TIMESTAMPTZ | Date + time + zone | '2026-07-15 14:30:00+00' |
| TIMESTAMP | Date + time (no zone) | Avoid; use TIMESTAMPTZ |
| INTERVAL | Duration | '1 year 2 months 3 days' |

```sql
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    event_date DATE NOT NULL,
    start_time TIME,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    duration INTERVAL DEFAULT '1 hour',
    expires_at TIMESTAMPTZ GENERATED ALWAYS AS (created_at + INTERVAL '30 days') STORED
);
```

### Boolean

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    is_urgent BOOLEAN DEFAULT FALSE
);
-- TRUE, FALSE, NULL
-- Aliases: 'yes'/'no', 'on'/'off', '1'/'0', 'true'/'false'
```

### Binary Data

```sql
CREATE TABLE files (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    content BYTEA,              -- Binary data
    content_hash BYTEA CHECK (OCTET_LENGTH(content_hash) = 32),  -- SHA-256
    size_bytes BIGINT
);
```

### UUID

```sql
-- Requires pgcrypto or uuid-ossp extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE api_keys (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    key_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- PostgreSQL 18+: UUIDv7 (time-ordered, index-friendly)
-- id UUID DEFAULT uuidv7() PRIMARY KEY
```

### Arrays

```sql
CREATE TABLE blog_posts (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    tags TEXT[] DEFAULT '{}',
    ratings INTEGER[] DEFAULT '{}',
    CHECK (array_length(tags, 1) <= 10)  -- Max 10 tags
);

-- Array operations
SELECT * FROM blog_posts WHERE tags @> ARRAY['postgresql'];
SELECT * FROM blog_posts WHERE 'sql' = ANY(tags);
SELECT * FROM blog_posts WHERE tags && ARRAY['sql', 'database'];  -- Overlap
UPDATE blog_posts SET tags = array_append(tags, 'new-tag') WHERE id = 1;
```

### JSON/JSONB

```sql
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    settings JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    CHECK (jsonb_typeof(settings) = 'object')
);

-- JSONB operators
SELECT settings->>'theme' FROM user_profiles;
SELECT * FROM user_profiles WHERE settings @> '{"notifications": true}';
SELECT * FROM user_profiles WHERE metadata ? 'premium';
```

### Range Types

```sql
CREATE TABLE room_bookings (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL,
    during TSTZRANGE NOT NULL,
    EXCLUDE USING gist (room_id WITH =, during WITH &&)
);

INSERT INTO room_bookings (room_id, during)
VALUES (1, '[2026-07-15 09:00, 2026-07-15 11:00)');

-- Range operators
SELECT * FROM room_bookings WHERE during @> '2026-07-15 10:00'::timestamptz;
SELECT * FROM room_bookings WHERE during && '[2026-07-15 10:00, 2026-07-15 12:00)';
```

### Enumerated Types

```sql
CREATE TYPE user_role AS ENUM ('admin', 'editor', 'viewer', 'guest');
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');

CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    status order_status DEFAULT 'pending',
    role user_role DEFAULT 'guest'
);

-- Adding values (PostgreSQL 16+: can add before/after existing)
ALTER TYPE order_status ADD VALUE 'refunded' AFTER 'delivered';
```

### Composite Types

```sql
CREATE TYPE address AS (
    street TEXT,
    city TEXT,
    postal_code VARCHAR(20),
    country VARCHAR(2)
);

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name TEXT,
    billing_address address,
    shipping_address address
);

-- Access composite fields
SELECT (billing_address).city FROM customers;
SELECT * FROM customers WHERE (billing_address).country = 'US';
```

### Domain Types

```sql
CREATE DOMAIN email AS VARCHAR(255)
    CHECK (VALUE ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

CREATE DOMAIN positive_integer AS INTEGER
    CHECK (VALUE > 0);

CREATE DOMAIN url AS TEXT
    CHECK (VALUE ~ '^https?://');

CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    email email NOT NULL UNIQUE,
    age positive_integer,
    website url
);
```

### Vector Search (pgvector) - Advanced Data Type

PostgreSQL's capabilities can be significantly extended for AI/ML workloads using `pgvector`. This allows storing and querying vector embeddings directly in your relational database, enabling highly performant similarity searches.

```sql
-- Ensure the extension is loaded
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE document_embeddings (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    -- Example: Storing 1536-dimensional embeddings (e.g., from OpenAI text-embedding-ada-002)
    embedding VECTOR(1536) 
);

-- Insert vector data
INSERT INTO document_embeddings (content, embedding) 
VALUES ('PostgreSQL is an advanced open-source database', '[0.11, 0.24, -0.35, ...]');

-- Vector similarity search operators:
-- <-> : L2 distance (Euclidean)
-- <#> : Negative Inner product
-- <=> : Cosine distance

-- Find the 5 most similar documents using Cosine Distance
SELECT id, content, 1 - (embedding <=> '[0.11, 0.24, -0.35, ...]') AS similarity_score
FROM document_embeddings 
ORDER BY embedding <=> '[0.11, 0.24, -0.35, ...]'
LIMIT 5;

-- To scale vector searches to millions of rows, index using HNSW (Hierarchical Navigable Small World)
CREATE INDEX ON document_embeddings USING hnsw (embedding vector_cosine_ops);
-- Note: IVFFlat is also available but HNSW generally provides superior recall and performance.
```

---

## DDL - Data Definition Language

### CREATE TABLE

```sql
CREATE TABLE employees (
    id BIGSERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email email NOT NULL UNIQUE,
    salary NUMERIC(12, 2) CHECK (salary > 0),
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    manager_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
    hire_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_names_not_empty CHECK (LENGTH(TRIM(first_name)) > 0),
    CONSTRAINT chk_valid_hire_date CHECK (hire_date <= CURRENT_DATE)
);
```

### Advanced: Table Partitioning

Partitioning is crucial for scaling massive tables. It splits a single logical table into multiple physical tables, radically improving query performance and data lifecycle management.

```sql
-- Create a partitioned table (declarative partitioning by RANGE)
CREATE TABLE measurement (
    city_id         int not null,
    logdate         date not null,
    peaktemp        int,
    unitsales       int
) PARTITION BY RANGE (logdate);

-- Create partitions for specific date ranges
CREATE TABLE measurement_y2026m01 PARTITION OF measurement
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE measurement_y2026m02 PARTITION OF measurement
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- Data inserted into the 'measurement' table is automatically routed 
-- to the correct underlying physical partition.
-- Querying 'measurement' transparently queries relevant partitions (Partition Pruning).

-- To age out old data instantly (O(1) complexity):
-- DROP TABLE measurement_y2020m01; 
```

### ALTER TABLE

```sql
-- Add column
ALTER TABLE employees ADD COLUMN phone VARCHAR(20);
ALTER TABLE employees ADD COLUMN bio TEXT CHECK (LENGTH(bio) <= 5000);

-- Drop column
ALTER TABLE employees DROP COLUMN IF EXISTS temp_column;

-- Rename column
ALTER TABLE employees RENAME COLUMN first_name TO given_name;

-- Change type
ALTER TABLE employees ALTER COLUMN salary TYPE NUMERIC(14, 2);

-- Add constraint
ALTER TABLE employees ADD CONSTRAINT fk_department 
    FOREIGN KEY (department_id) REFERENCES departments(id);

-- Add constraint without validating existing data (fast on large tables)
ALTER TABLE employees ADD CONSTRAINT chk_email_format 
    CHECK (email ~ '@') NOT VALID;
ALTER TABLE employees VALIDATE CONSTRAINT chk_email_format;

-- Drop constraint
ALTER TABLE employees DROP CONSTRAINT IF EXISTS chk_email_format;

-- Rename table
ALTER TABLE employees RENAME TO staff_members;

-- Set/Drop default
ALTER TABLE employees ALTER COLUMN is_active SET DEFAULT TRUE;
ALTER TABLE employees ALTER COLUMN is_active DROP DEFAULT;

-- Set NOT NULL
ALTER TABLE employees ALTER COLUMN email SET NOT NULL;

-- Add column with default (fills existing rows)
ALTER TABLE employees ADD COLUMN country VARCHAR(2) DEFAULT 'US';
```

### DROP & TRUNCATE

```sql
-- Drop table
DROP TABLE IF EXISTS temp_data CASCADE;

-- Truncate (fast, minimal logging, resets identity)
TRUNCATE TABLE audit_logs RESTART IDENTITY CASCADE;
```

---

## DCL & Security Hardening

### Role-Based Access Control (RBAC)

Applying the Principle of Least Privilege is essential. Do not run application queries as a superuser.

```sql
-- Create functional roles (groups)
CREATE ROLE read_only;
CREATE ROLE read_write;

-- Grant minimal necessary permissions
GRANT CONNECT ON DATABASE my_db TO read_only;
GRANT USAGE ON SCHEMA public TO read_only;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO read_only;
-- Automatically grant SELECT on future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO read_only;

-- Elevate read_write
GRANT read_only TO read_write;
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO read_write;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO read_write;

-- Create an actual user and assign the role
CREATE USER api_worker WITH PASSWORD 'secure_password';
GRANT read_write TO api_worker;
```

### Row-Level Security (RLS)

RLS enforces security at the table row level, making multi-tenant applications inherently secure directly at the database layer.

```sql
-- Enable RLS on a table
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Create a policy allowing users to read ONLY their own profile
CREATE POLICY "Users can view own profile" 
    ON user_profiles
    FOR SELECT
    USING (user_id = current_user_id_function()); -- Custom function to get context

-- Enforce policies even for table owners
ALTER TABLE user_profiles FORCE ROW LEVEL SECURITY;
```

### Security Hardening Best Practices

1. **pg_hba.conf**: The Host-Based Authentication configuration file. Strictly whitelist IPs and mandate TLS/SSL.
   ```text
   # Require SSL and scram-sha-256 password auth for all remote connections
   hostssl    all             all             0.0.0.0/0               scram-sha-256
   ```
2. **Password Encryption**: Always use `scram-sha-256`, never `md5` (which is vulnerable).
3. **Audit Logging**: Use the `pgaudit` extension for granular, compliance-ready logging of sensitive operations.

---

## DML - Data Manipulation Language

### INSERT

```sql
-- Single row
INSERT INTO employees (first_name, last_name, email, salary)
VALUES ('Alice', 'Johnson', 'alice@company.com', 85000);

-- Multiple rows
INSERT INTO employees (first_name, last_name, email, salary)
VALUES 
    ('Bob', 'Smith', 'bob@company.com', 75000),
    ('Carol', 'Davis', 'carol@company.com', 92000),
    ('David', 'Wilson', 'david@company.com', 68000);

-- Insert from SELECT
INSERT INTO employees_archive (id, first_name, last_name, email, hire_date)
SELECT id, first_name, last_name, email, hire_date
FROM employees
WHERE is_active = FALSE;

-- RETURNING clause
INSERT INTO employees (first_name, last_name, email)
VALUES ('Eve', 'Brown', 'eve@company.com')
RETURNING id, created_at;

-- Upsert (ON CONFLICT)
INSERT INTO employees (id, first_name, last_name, email, salary)
VALUES (1, 'Alice', 'Updated', 'alice.new@company.com', 90000)
ON CONFLICT (id) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    email = EXCLUDED.email,
    salary = EXCLUDED.salary,
    updated_at = CURRENT_TIMESTAMP;

-- Upsert with WHERE condition
INSERT INTO employees (email, first_name, last_name)
VALUES ('alice@company.com', 'Alice', 'Johnson')
ON CONFLICT (email) DO UPDATE SET
    first_name = EXCLUDED.first_name
WHERE employees.updated_at < EXCLUDED.updated_at;

-- ON CONFLICT DO NOTHING
INSERT INTO employees (email, first_name, last_name)
VALUES ('alice@company.com', 'Alice', 'Johnson')
ON CONFLICT (email) DO NOTHING
RETURNING id;
```

### SELECT

```sql
-- Basic
SELECT * FROM employees;
SELECT first_name, last_name, email FROM employees;

-- Aliases
SELECT 
    first_name AS fname,
    last_name AS lname,
    salary * 12 AS annual_salary,
    salary / 12 AS monthly_salary
FROM employees;

-- DISTINCT
SELECT DISTINCT department_id FROM employees;

-- DISTINCT ON (PostgreSQL specific - first row per group)
SELECT DISTINCT ON (department_id)
    department_id, first_name, last_name, salary
FROM employees
ORDER BY department_id, salary DESC;

-- LIMIT / OFFSET (pagination)
SELECT * FROM employees ORDER BY id LIMIT 10 OFFSET 0;   -- Page 1
SELECT * FROM employees ORDER BY id LIMIT 10 OFFSET 10;  -- Page 2
SELECT * FROM employees ORDER BY id LIMIT 10 OFFSET 20;  -- Page 3

-- FETCH FIRST (SQL standard)
SELECT * FROM employees ORDER BY salary DESC FETCH FIRST 5 ROWS WITH TIES;

-- ORDER BY
SELECT * FROM employees ORDER BY last_name ASC, first_name ASC;
SELECT * FROM employees ORDER BY salary DESC NULLS LAST;

-- WHERE
SELECT * FROM employees WHERE salary > 70000;
SELECT * FROM employees WHERE department_id = 1 AND salary > 70000;
SELECT * FROM employees WHERE department_id IN (1, 2, 3);
SELECT * FROM employees WHERE salary BETWEEN 50000 AND 80000;
SELECT * FROM employees WHERE last_name LIKE 'S%';
SELECT * FROM employees WHERE email LIKE '%@company.com';
SELECT * FROM employees WHERE first_name ILIKE 'alice';  -- Case-insensitive
SELECT * FROM employees WHERE phone IS NULL;
SELECT * FROM employees WHERE phone IS NOT NULL;
SELECT * FROM employees WHERE email ~ '^[a-z]+@company\.com$';
SELECT * FROM employees WHERE last_name ~* 'smith|johnson';
```

### UPDATE

```sql
-- Single column
UPDATE employees SET salary = salary * 1.05 WHERE department_id = 1;

-- Multiple columns
UPDATE employees 
SET salary = 85000, is_active = TRUE, updated_at = CURRENT_TIMESTAMP
WHERE id = 5;

-- Update from another table
UPDATE employees e
SET salary = s.new_salary
FROM salary_adjustments s
WHERE e.id = s.employee_id;

-- Update with RETURNING
UPDATE employees SET salary = salary * 1.10 WHERE department_id = 2
RETURNING id, first_name, last_name, salary;
```

### DELETE

```sql
-- Delete specific rows
DELETE FROM employees WHERE is_active = FALSE;

-- Delete all (slow, logs each row, fires triggers)
DELETE FROM employees;

-- Delete with RETURNING
DELETE FROM employees WHERE id = 10 RETURNING *;

-- Delete using another table
DELETE FROM employees e
USING departments d
WHERE e.department_id = d.id AND d.name = 'Closed';
```

---

## Operators Reference

### Comparison

| Operator | Meaning |
|----------|---------|
| `=` | Equal |
| `<>` or `!=` | Not equal |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less than or equal |
| `>=` | Greater than or equal |
| `BETWEEN` | Inclusive range |
| `IN` | Match any in list |
| `NOT IN` | Not in list |
| `LIKE` | Pattern match (% = any, _ = one) |
| `ILIKE` | Case-insensitive LIKE |
| `SIMILAR TO` | SQL regex |
| `~` | POSIX regex match |
| `~*` | Case-insensitive regex |
| `!~` | Not regex match |
| `IS NULL` | Null test |
| `IS NOT NULL` | Not null test |
| `IS DISTINCT FROM` | Null-safe comparison |
| `IS NOT DISTINCT FROM` | Null-safe equality |

### Logical

```sql
SELECT * FROM employees 
WHERE (salary > 70000 OR department_id = 1) 
  AND is_active = TRUE
  AND NOT (hire_date < '2020-01-01');
```

### Mathematical

```sql
SELECT 
    10 + 5, 10 - 5, 10 * 5, 10 / 3,       -- Basic
    10.0 / 3,                              -- Float division
    10 % 3,                                -- Modulo
    2 ^ 3,                                 -- Exponent
    |/ 16,                                 -- Square root
    ||/ 27,                                -- Cube root
    @ -5,                                  -- Absolute value
    5 !,                                   -- Factorial
    RANDOM(),                              -- 0.0 to 1.0
    TRUNC(RANDOM() * 100);                -- Random integer 0-99
```

---

## Functions Reference

### String Functions

```sql
SELECT 
    CONCAT('Hello', ' ', 'World'),              -- 'Hello World'
    'Hello' || ' ' || 'World',                  -- Concatenation
    LENGTH('Hello'),                             -- 5
    CHAR_LENGTH('Hello'),                        -- 5 (same)
    OCTET_LENGTH('Hello'),                       -- 5 (bytes)
    SUBSTRING('Hello World' FROM 1 FOR 5),      -- 'Hello'
    SUBSTR('Hello World', 1, 5),                -- 'Hello'
    LEFT('Hello World', 5),                      -- 'Hello'
    RIGHT('Hello World', 5),                     -- 'World'
    UPPER('hello'),                              -- 'HELLO'
    LOWER('HELLO'),                              -- 'hello'
    INITCAP('hello world'),                      -- 'Hello World'
    TRIM('  hello  '),                           -- 'hello'
    TRIM(BOTH 'x' FROM 'xxxhelloxxx'),          -- 'hello'
    LTRIM('  hello'),                             -- 'hello'
    RTRIM('hello  '),                             -- 'hello'
    REPLACE('hello world', 'world', 'postgres'), -- 'hello postgres'
    TRANSLATE('hello', 'eo', '00'),             -- 'h0ll0'
    POSITION('lo' IN 'hello'),                   -- 4
    STRPOS('hello', 'lo'),                       -- 4
    SPLIT_PART('a,b,c', ',', 2),                -- 'b'
    STRING_TO_ARRAY('a,b,c', ','),              -- {'a','b','c'}
    ARRAY_TO_STRING(ARRAY['a','b','c'], ','),   -- 'a,b,c'
    REVERSE('hello'),                           -- 'olleh'
    MD5('password'),                            -- Hash
    SHA256('password'),                         -- Hash
    ENCODE(DIGEST('password', 'sha256'), 'hex'),-- Hash (pgcrypto)
    LPAD('42', 5, '0'),                         -- '00042'
    RPAD('42', 5, '0'),                         -- '42000'
    REPEAT('ab', 3),                            -- 'ababab'
    CHR(65),                                    -- 'A'
    ASCII('A'),                                 -- 65
    FORMAT('Hello %s, you have %s messages', 'Alice', 5);
```

### Numeric Functions

```sql
SELECT 
    ROUND(3.14159, 2),          -- 3.14
    ROUND(3.5),                  -- 4 (to integer)
    TRUNC(3.14159, 2),           -- 3.14
    TRUNC(3.9),                  -- 3 (toward zero)
    CEIL(3.2),                   -- 4
    FLOOR(3.8),                  -- 3
    ABS(-10),                    -- 10
    SIGN(-10),                   -- -1
    MOD(10, 3),                  -- 1
    POWER(2, 3),                 -- 8
    SQRT(16),                    -- 4
    CBRT(27),                    -- 3
    EXP(1),                      -- e
    LN(10),                      -- natural log
    LOG(100),                    -- log base 10
    LOG(2, 8),                   -- log base 2
    PI(),                        -- 3.14159...
    DEGREES(PI()),               -- 180
    RADIANS(180),                -- PI
    SIN(0), COS(0), TAN(0),      -- Trig
    ASIN(1), ACOS(1), ATAN(1),   -- Inverse trig
    ATAN2(1, 1),                 -- Angle from origin
    WIDTH_BUCKET(5, 0, 10, 5);   -- Histogram bucket (returns 3)
```

### Date/Time Functions

```sql
SELECT 
    CURRENT_DATE,                           -- Date
    CURRENT_TIME,                           -- Time with zone
    CURRENT_TIMESTAMP,                      -- Timestamp with zone
    NOW(),                                  -- Same
    LOCALTIME,                              -- Time without zone
    LOCALTIMESTAMP,                         -- Timestamp without zone
    TIMEOFDAY(),                            -- Text representation
    CLOCK_TIMESTAMP(),                      -- Real-time (changes during query)
    STATEMENT_TIMESTAMP(),                  -- Start of current statement
    TRANSACTION_TIMESTAMP(),                -- Start of current transaction
    AGE('1990-05-15'),                      -- Interval since birth
    AGE('2026-01-01', '1990-05-15'),        -- Interval between dates
    DATE_PART('year', '2026-07-15'::DATE),  -- 2026
    DATE_PART('quarter', '2026-07-15'::DATE),-- 3
    DATE_PART('week', '2026-07-15'::DATE),  -- ISO week number
    EXTRACT(EPOCH FROM NOW()),              -- Unix timestamp
    EXTRACT(YEAR FROM NOW()),
    EXTRACT(MONTH FROM NOW()),
    EXTRACT(DAY FROM NOW()),
    EXTRACT(DOW FROM NOW()),                -- Day of week (0=Sunday)
    EXTRACT(ISODOW FROM NOW()),             -- ISO day (1=Monday)
    EXTRACT(WEEK FROM NOW()),               -- ISO week
    TO_CHAR(CURRENT_DATE, 'YYYY-MM-DD'),    -- Format as text
    TO_CHAR(NOW(), 'YYYY-MM-DD HH24:MI:SS TZ'),
    TO_DATE('2026-07-15', 'YYYY-MM-DD'),    -- Parse date
    TO_TIMESTAMP('2026-07-15 14:30:00', 'YYYY-MM-DD HH24:MI:SS'),
    DATE_TRUNC('month', NOW()),             -- First of month
    DATE_TRUNC('week', NOW()),              -- Monday of this week
    DATE_TRUNC('day', NOW()),               -- Midnight today
    (CURRENT_DATE + INTERVAL '1 month')::DATE,
    CURRENT_DATE + 7,                        -- Add days
    CURRENT_DATE - INTERVAL '1 year',
    NOW() + INTERVAL '1 hour 30 minutes',
    JUSTIFY_DAYS(INTERVAL '35 days'),       -- 1 mon 5 days
    JUSTIFY_HOURS(INTERVAL '27 hours'),     -- 1 day 3 hours
    MAKE_DATE(2026, 7, 15),
    MAKE_TIME(14, 30, 0),
    MAKE_TIMESTAMP(2026, 7, 15, 14, 30, 0),
    MAKE_INTERVAL(days => 7),
    ISFINITE('2026-07-15'::DATE);           -- TRUE (not infinity)
```

### Conditional & Utility

```sql
SELECT 
    COALESCE(NULL, NULL, 'fallback', 'other'),  -- 'fallback'
    NULLIF(10, 10),                              -- NULL
    NULLIF(10, 5),                               -- 10
    GREATEST(1, 5, 3, 9, 2),                     -- 9
    LEAST(1, 5, 3, 9, 2),                        -- 1
    CASE 
        WHEN salary > 100000 THEN 'High'
        WHEN salary > 60000 THEN 'Medium'
        ELSE 'Low'
    END,
    CASE department_id
        WHEN 1 THEN 'Engineering'
        WHEN 2 THEN 'Sales'
        ELSE 'Other'
    END,
    DECODE(department_id, 1, 'Eng', 2, 'Sales', 'Other'),  -- Oracle compat
    IF(salary > 80000, 'High Earner', 'Standard'),          -- Not standard SQL
    COALESCE(NULLIF(TRIM(email), ''), 'no-email@example.com');
```

---

## GROUP BY, HAVING, Aggregates

### Aggregate Functions

```sql
SELECT 
    COUNT(*) AS total_rows,
    COUNT(email) AS non_null_emails,
    COUNT(DISTINCT department_id) AS unique_depts,
    SUM(salary) AS total_payroll,
    AVG(salary) AS avg_salary,
    AVG(salary)::NUMERIC(12,2) AS avg_salary_rounded,
    MAX(salary) AS highest,
    MIN(salary) AS lowest,
    STRING_AGG(first_name, ', ' ORDER BY first_name) AS names,
    ARRAY_AGG(salary ORDER BY salary DESC) AS salaries,
    JSON_AGG(
        jsonb_build_object('name', first_name, 'salary', salary)
        ORDER BY salary DESC
    ) AS employees_json,
    JSON_OBJECT_AGG(first_name, salary) AS salary_map,
    BOOL_AND(is_active),                    -- TRUE if all active
    BOOL_OR(is_active),                     -- TRUE if any active
    EVERY(is_active),                       -- Same as BOOL_AND
    CORR(salary, years_experience),         -- Correlation coefficient
    REGR_R2(salary, years_experience),      -- R-squared
    MODE() WITHIN GROUP (ORDER BY salary)   -- Most common salary
FROM employees;
```

### GROUP BY

```sql
-- Basic
SELECT department_id, COUNT(*), AVG(salary)
FROM employees
GROUP BY department_id;

-- Multiple columns
SELECT department_id, is_active, COUNT(*), AVG(salary)
FROM employees
GROUP BY department_id, is_active;

-- HAVING (filter aggregates)
SELECT department_id, COUNT(*) AS c, AVG(salary) AS avg_sal
FROM employees
GROUP BY department_id
HAVING COUNT(*) > 5 AND AVG(salary) > 60000;

-- ROLLUP (subtotals)
SELECT COALESCE(department_id::TEXT, 'All') AS dept,
       COALESCE(job_title, 'All') AS title,
       COUNT(*), SUM(salary)
FROM employees
GROUP BY ROLLUP(department_id, job_title);

-- CUBE (all combinations)
SELECT department_id, job_title, COUNT(*)
FROM employees
GROUP BY CUBE(department_id, job_title);

-- GROUPING SETS (custom combinations)
SELECT department_id, job_title, COUNT(*)
FROM employees
GROUP BY GROUPING SETS (
    (department_id, job_title),
    (department_id),
    (job_title),
    ()
);
```

---

## Advanced Architecture & Administration

Scaling PostgreSQL for production requires external tools and architectural patterns.

### Connection Pooling (PgBouncer)

PostgreSQL spawns a process for every connection, which is memory intensive (~10MB+ per connection). In highly concurrent environments (e.g., Serverless functions, heavy web traffic), connection pooling is mandatory.

- **PgBouncer**: The industry standard lightweight connection pooler.
- **Pgpool-II**: Provides pooling plus load balancing, query caching, and automated failover.
- **Modes**:
  - `Session Pooling`: Connection assigned per client session.
  - `Transaction Pooling`: (Most common) Connection assigned per transaction, allowing thousands of clients to share a small pool of database connections seamlessly.

### Replication & High Availability

PostgreSQL natively supports robust replication strategies.

- **Physical Streaming Replication**: Exact block-by-block mirror of the primary database. Used for creating Read Replicas (Hot Standby) to offload read-heavy queries.
- **Logical Replication**: Replicates data on a per-table basis using a Publisher/Subscriber model. Ideal for upgrading major versions with zero downtime, or synchronizing specific tables to a data warehouse.
- **High Availability (HA) Managers**: Tools like Patroni or repmgr automate failover, promoting a replica to primary if the primary server goes down.

### Disaster Recovery & Backups

Simple `pg_dump` is insufficient for large databases.

- **WAL (Write-Ahead Logging)**: PostgreSQL records every transaction to a WAL file before writing to data files.
- **PITR (Point-In-Time Recovery)**: By archiving WAL files continuously (e.g., to an S3 bucket) alongside base backups, you can restore the database to the precise microsecond before a catastrophic error (like accidentally dropping a critical table).
- **pgBackRest / WAL-G**: Enterprise-grade backup tools that handle incremental backups, parallel compression, and WAL archiving natively to cloud storage.

### Cloud Deployment & Serverless

Modern PostgreSQL deployments often leverage managed cloud infrastructure.

- **Managed Services**: AWS RDS, Google Cloud SQL, Azure Database for PostgreSQL provide automated backups, patching, and click-to-deploy read replicas.
- **Aurora/AlloyDB**: Cloud-native architectures that decouple storage from compute, offering immense scalability and fast failovers.
- **Serverless PostgreSQL (Neon, Supabase)**: Automatically scale compute resources to zero when idle and provision them instantly on demand. They heavily utilize branching (similar to Git) for database schema isolation.

---
*Previous: 02 - Installation | Next: 04 - Joins & Relationships*
