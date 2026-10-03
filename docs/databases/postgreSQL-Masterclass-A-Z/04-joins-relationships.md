# 04 - Joins & Relationships

> Complete guide to SQL JOINs, relationship modeling, referential integrity, and practical query patterns. Dive deep into architectural considerations, performance, scaling, and advanced concepts like Vector Search (pgvector), Row-Level Security (RLS), and Table Partitioning.

---

## 1. Advanced Relationship Modeling & Architecture

### One-to-One
```text
users ──────── user_profiles
 id (PK)        user_id (PK, FK)
 email          bio
 password       avatar_url
```
**Architectural Context:** 
- **Denormalization vs. Normalization:** While 1:1 relationships are great for logical separation, consider denormalizing into a single table with `JSONB` for optional profile data to avoid the `JOIN` penalty in high-throughput microservices.
- **Security:** Sometimes 1:1 is used purely for security hardening—separating PII (Personally Identifiable Information) or authentication credentials into a strictly controlled table, while keeping public profile data in a broadly accessible table.

### One-to-Many
```text
departments ──────── employees
 id (PK)              id (PK)
 name                 department_id (FK)
 budget               name
                      salary
```
**Crucial Best Practice:** PostgreSQL **does NOT** automatically index foreign keys. Always manually create an index on `department_id` to prevent sequential scans during `JOIN` operations and to optimize cascading deletes.

### Many-to-Many
```text
students ───── enrollments ───── courses
 id (PK)       student_id (FK)    id (PK)
 name          course_id (FK)     title
               grade              credits
               PRIMARY KEY (student_id, course_id)
```
**Scaling at the Edge:** When join tables (like `enrollments`) grow to billions of rows, they become massive bottlenecks. Use **Declarative Table Partitioning** (e.g., partitioning by `semester` or `year`) to keep index sizes manageable, ensuring `INSERT` and `JOIN` operations remain fast over time.

---

## 2. Setup Example Data (Enhanced)

We'll set up our schema including standard relationships, and also weave in **pgvector** for AI-driven similarity matching and foundational **Row-Level Security (RLS)**.

```sql
-- Enable vector extension for ML/AI similarity search
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    budget NUMERIC(12, 2)
);

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    salary NUMERIC(10, 2) CHECK (salary > 0),
    hire_date DATE DEFAULT CURRENT_DATE,
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    manager_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    -- Advanced: Vector embedding for employee skills/profile matching
    skills_embedding vector(3) 
);

-- ALWAYS index your foreign keys!
CREATE INDEX idx_employees_department_id ON employees(department_id);
CREATE INDEX idx_employees_manager_id ON employees(manager_id);

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    start_date DATE,
    end_date DATE,
    budget NUMERIC(12, 2)
);

CREATE TABLE employee_projects (
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    role VARCHAR(50),
    hours_allocated INTEGER CHECK (hours_allocated > 0),
    PRIMARY KEY (employee_id, project_id)
);

-- Insert sample data
INSERT INTO departments (name, location, budget) VALUES
    ('Engineering', 'Building A', 2000000),
    ('Sales', 'Building B', 1500000),
    ('Marketing', 'Building B', 800000),
    ('HR', 'Building A', 400000),
    ('Finance', 'Building C', 1000000);

-- Mocking 3D vectors for simplicity: [Backend, Frontend, DevOps]
INSERT INTO employees (first_name, last_name, email, salary, department_id, manager_id, skills_embedding) VALUES
    ('Alice', 'Johnson', 'alice@company.com', 95000, 1, NULL, '[0.9, 0.1, 0.8]'),
    ('Bob', 'Smith', 'bob@company.com', 80000, 1, 1, '[0.8, 0.8, 0.2]'),
    ('Carol', 'Davis', 'carol@company.com', 75000, 1, 2, '[0.2, 0.9, 0.1]'),
    ('David', 'Wilson', 'david@company.com', 72000, 1, 2, '[0.5, 0.5, 0.5]'),
    ('Eve', 'Brown', 'eve@company.com', 65000, 2, 1, '[0.1, 0.1, 0.1]');

INSERT INTO projects (name, start_date, end_date, budget) VALUES
    ('Website Redesign', '2026-01-01', '2026-06-30', 50000),
    ('Data Migration', '2026-02-01', '2026-05-31', 30000);

INSERT INTO employee_projects (employee_id, project_id, role, hours_allocated) VALUES
    (2, 1, 'Tech Lead', 200), 
    (3, 1, 'Developer', 300),
    (1, 2, 'Architect', 100);
```

---

## 3. JOIN Types & Execution Strategies

### Standard JOINs

#### INNER JOIN
Returns only matching rows from both tables.
```sql
SELECT e.first_name, e.last_name, e.salary, d.name AS department
FROM employees e
INNER JOIN departments d ON e.department_id = d.id;
```

#### LEFT JOIN
Returns all left rows + matched right rows (NULL for unmatched). Ideal for finding missing relationships.
```sql
-- All employees with dept info
SELECT e.first_name, e.last_name, COALESCE(d.name, 'No Dept') AS department
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id;

-- Departments with no employees (Anti-Join Pattern)
SELECT d.name
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id
WHERE e.id IS NULL;
```

#### FULL JOIN
Returns all rows from both tables. Useful for data reconciliation.
```sql
-- Find orphaned records both ways
SELECT e.first_name, e.last_name, d.name
FROM employees e
FULL JOIN departments d ON e.department_id = d.id
WHERE e.id IS NULL OR d.id IS NULL;
```

#### SELF JOIN
Table joined to itself (e.g., hierarchical data).
```sql
-- Employee and their manager
SELECT 
    e.first_name AS employee,
    m.first_name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;
```

### Advanced JOINs

#### LATERAL JOIN (SQL's "For-Each" Loop)
A `LATERAL` join allows a subquery in the `FROM` clause to reference columns from preceding items in the `FROM` list. It is incredibly powerful for top-N queries per category.
```sql
-- Get the top 2 highest paid employees for EACH department
SELECT d.name AS department, top_emp.first_name, top_emp.salary
FROM departments d
CROSS JOIN LATERAL (
    SELECT first_name, salary
    FROM employees e
    WHERE e.department_id = d.id
    ORDER BY salary DESC
    LIMIT 2
) top_emp;
```

#### Vector Similarity JOIN (pgvector)
Using distance operators (e.g., `<->` for L2 distance, `<#>` for inner product) to find related records via embeddings.
```sql
-- Find the 2 employees with the most similar skill sets to Bob (id=2)
SELECT e2.first_name, e2.skills_embedding <-> e1.skills_embedding AS distance
FROM employees e1
JOIN employees e2 ON e1.id != e2.id
WHERE e1.id = 2
ORDER BY e1.skills_embedding <-> e2.skills_embedding
LIMIT 2;
```

### Under the Hood: PostgreSQL JOIN Algorithms
When you run a `JOIN`, the query planner picks one of three physical algorithms (visible via `EXPLAIN ANALYZE`):
1. **Nested Loop Join:** Iterates through the left table row-by-row and looks up the right table. Fast for small datasets or when highly selective indexes are used.
2. **Hash Join:** Hashes the smaller table in memory, then scans the larger table to probe the hash table. Excellent for large, unsorted datasets.
3. **Merge Join:** Sorts both tables on the join key (or uses existing indexes), then merges them. Highly efficient for massive datasets that are already indexed/sorted.

---

## 4. Referential Integrity, Locking & Concurrency

### ON DELETE Actions

| Action | Behavior |
|--------|----------|
| CASCADE | Delete child rows when parent deleted |
| SET NULL | Set FK to NULL |
| SET DEFAULT | Set FK to default value |
| RESTRICT | Prevent parent deletion if children exist (immediate) |
| NO ACTION | Like RESTRICT but checked at end of transaction |

### The Danger of CASCADE in Production
When `ON DELETE CASCADE` fires, PostgreSQL must acquire **Row Exclusive Locks** on all affected child rows. 
- **Connection Pooling (PgBouncer):** In highly concurrent systems using PgBouncer in transaction mode, a single delete on a parent table that cascades to millions of child rows can block other transactions and exhaust the connection pool.
- **Disaster Recovery / Replication:** Cascading deletes generate massive amounts of WAL (Write-Ahead Log) data. In Logical Replication setups, cascading deletes are replayed row-by-row on the subscriber, which can lead to severe replication lag. 
- **Best Practice:** For large tables, prefer soft-deletes (e.g., `deleted_at TIMESTAMP`) or perform batched background deletes using a cron job (like `pg_cron`) instead of relying solely on synchronous `CASCADE`.

---

## 5. Security Hardening: Row-Level Security (RLS)

When performing JOINs, you might expose data that users shouldn't see. PostgreSQL's RLS ensures users only see data they own, natively integrating with JOINs.

```sql
-- Enable RLS
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE employee_projects ENABLE ROW LEVEL SECURITY;

-- Create an RBAC Policy: Users can only see projects they are assigned to
CREATE POLICY project_access_policy ON projects
    FOR SELECT 
    USING (
        id IN (
            SELECT project_id 
            FROM employee_projects 
            WHERE employee_id = current_setting('app.current_user_id')::int
        )
    );
```
With RLS enabled, even if an application runs a `SELECT * FROM projects`, PostgreSQL rewrites the execution plan to strictly filter rows based on the underlying JOIN defined in the security policy.

---

## 6. Scaling and Cloud Deployment

When analytical queries involving 5+ tables bring your primary database to a crawl:
- **Read Replicas:** Route heavy `JOIN` reporting queries to Read Replicas (via streaming physical replication). Tools like PgBouncer or proxy routers (Pgpool-II) can automatically route `SELECT` queries to replicas while keeping `INSERT/UPDATE` on the primary.
- **Materialized Views:** If your JOIN logic is complex and data doesn't need to be strictly real-time, bake the JOINs into a `MATERIALIZED VIEW` and refresh it concurrently.

---

## 7. Practical Advanced Examples

### Complex Department Analytics (CTEs + JOINs)
Using Common Table Expressions (CTEs) for readable, modular complex queries.

```sql
WITH dept_stats AS (
    SELECT 
        department_id,
        COUNT(id) AS employee_count,
        COALESCE(AVG(salary), 0) AS avg_salary
    FROM employees
    GROUP BY department_id
),
project_stats AS (
    SELECT 
        e.department_id,
        SUM(ep.hours_allocated) AS total_hours
    FROM employee_projects ep
    JOIN employees e ON ep.employee_id = e.id
    GROUP BY e.department_id
)
SELECT 
    d.name AS department,
    d.location,
    ds.employee_count,
    ds.avg_salary::NUMERIC(10,2),
    COALESCE(ps.total_hours, 0) AS project_hours
FROM departments d
LEFT JOIN dept_stats ds ON d.id = ds.department_id
LEFT JOIN project_stats ps ON d.id = ps.department_id
ORDER BY ds.employee_count DESC NULLS LAST;
```

---
*Previous: 03 - SQL Fundamentals | Next: 05 - Constraints & Data Integrity*
