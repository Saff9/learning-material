# 04 - Joins & Relationships

> Complete guide to SQL JOINs, relationship modeling, referential integrity, and practical query patterns.

---

## Relationship Types

### One-to-One
```
users ──────── user_profiles
 id (PK)        user_id (PK, FK)
 email          bio
 password       avatar_url
```

### One-to-Many
```
departments ──────── employees
 id (PK)              id (PK)
 name                 department_id (FK)
 budget               name
                      salary
```

### Many-to-Many
```
students ───── enrollments ───── courses
 id (PK)       student_id (FK)    id (PK)
 name          course_id (FK)     title
               grade              credits
               PRIMARY KEY (student_id, course_id)
```

---

## Setup Example Data

```sql
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
    is_active BOOLEAN DEFAULT TRUE
);

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

INSERT INTO employees (first_name, last_name, email, salary, department_id, manager_id) VALUES
    ('Alice', 'Johnson', 'alice@company.com', 95000, 1, NULL),
    ('Bob', 'Smith', 'bob@company.com', 80000, 1, 1),
    ('Carol', 'Davis', 'carol@company.com', 75000, 1, 2),
    ('David', 'Wilson', 'david@company.com', 72000, 1, 2),
    ('Eve', 'Brown', 'eve@company.com', 65000, 2, 1),
    ('Frank', 'Miller', 'frank@company.com', 60000, 2, 5),
    ('Grace', 'Lee', 'grace@company.com', 58000, 2, 5),
    ('Henry', 'Taylor', 'henry@company.com', 70000, 3, 1),
    ('Ivy', 'Anderson', 'ivy@company.com', 55000, 3, 8),
    ('Jack', 'Thomas', 'jack@company.com', 85000, 5, 1);

INSERT INTO projects (name, start_date, end_date, budget) VALUES
    ('Website Redesign', '2026-01-01', '2026-06-30', 50000),
    ('Mobile App', '2026-03-01', '2026-12-31', 120000),
    ('Data Migration', '2026-02-01', '2026-05-31', 30000),
    ('Cloud Migration', '2026-04-01', '2026-10-31', 200000);

INSERT INTO employee_projects (employee_id, project_id, role, hours_allocated) VALUES
    (2, 1, 'Tech Lead', 200), (3, 1, 'Developer', 300),
    (4, 1, 'Developer', 300), (2, 2, 'Tech Lead', 400),
    (3, 2, 'Developer', 500), (5, 3, 'PM', 100),
    (8, 3, 'Coordinator', 150), (2, 4, 'Architect', 300),
    (10, 4, 'Analyst', 200);
```

---

## JOIN Types

### INNER JOIN
Returns only matching rows from both tables.

```sql
SELECT e.first_name, e.last_name, e.salary, d.name AS department
FROM employees e
INNER JOIN departments d ON e.department_id = d.id;
```

### LEFT JOIN
Returns all left rows + matched right rows (NULL for unmatched).

```sql
-- All employees with dept info
SELECT e.first_name, e.last_name, COALESCE(d.name, 'No Dept') AS department
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id;

-- Employees without a department
SELECT e.first_name, e.last_name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id
WHERE d.id IS NULL;

-- Departments with no employees
SELECT d.name
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id
WHERE e.id IS NULL;
```

### RIGHT JOIN
Returns all right rows + matched left rows. Rarely used — swap tables and use LEFT JOIN instead.

```sql
SELECT e.first_name, d.name
FROM employees e
RIGHT JOIN departments d ON e.department_id = d.id;
```

### FULL JOIN
Returns all rows from both tables.

```sql
SELECT e.first_name, e.last_name, d.name AS department
FROM employees e
FULL JOIN departments d ON e.department_id = d.id;

-- Find orphaned records both ways
SELECT e.first_name, e.last_name, d.name
FROM employees e
FULL JOIN departments d ON e.department_id = d.id
WHERE e.id IS NULL OR d.id IS NULL;
```

### CROSS JOIN
Cartesian product — every combination.

```sql
SELECT e.first_name, d.name
FROM employees e
CROSS JOIN departments d;
-- 10 employees * 5 departments = 50 rows
```

### SELF JOIN
Table joined to itself.

```sql
-- Employee and their manager
SELECT 
    e.first_name || ' ' || e.last_name AS employee,
    m.first_name || ' ' || m.last_name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;

-- Employees earning more than their manager
SELECT e.first_name, e.salary, m.first_name, m.salary
FROM employees e
JOIN employees m ON e.manager_id = m.id
WHERE e.salary > m.salary;
```

---

## Multiple JOINs

```sql
-- Employees + departments + managers
SELECT 
    e.id,
    e.first_name || ' ' || e.last_name AS employee,
    d.name AS department,
    m.first_name || ' ' || m.last_name AS manager
FROM employees e
JOIN departments d ON e.department_id = d.id
LEFT JOIN employees m ON e.manager_id = m.id;

-- Employees + departments + projects
SELECT 
    e.first_name || ' ' || e.last_name AS employee,
    d.name AS department,
    p.name AS project,
    ep.role,
    ep.hours_allocated
FROM employees e
JOIN departments d ON e.department_id = d.id
LEFT JOIN employee_projects ep ON e.id = ep.employee_id
LEFT JOIN projects p ON ep.project_id = p.id
ORDER BY e.last_name, p.name;
```

---

## Referential Integrity

### ON DELETE Actions

| Action | Behavior |
|--------|----------|
| CASCADE | Delete child rows when parent deleted |
| SET NULL | Set FK to NULL |
| SET DEFAULT | Set FK to default value |
| RESTRICT | Prevent parent deletion if children exist |
| NO ACTION | Like RESTRICT but checked at end of transaction |

```sql
-- CASCADE example
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE
);

-- SET NULL example
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL
);

-- Deferred constraints (allow circular refs in a transaction)
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER REFERENCES accounts(id) 
        DEFERRABLE INITIALLY DEFERRED
);

BEGIN;
INSERT INTO accounts (id, name, parent_id) VALUES (1, 'Root', 2);
INSERT INTO accounts (id, name, parent_id) VALUES (2, 'Child', 1);
COMMIT;  -- Constraints checked at commit
```

---

## Practical Examples

### Department Report

```sql
SELECT 
    d.name AS department,
    d.location,
    COUNT(e.id) AS employee_count,
    COALESCE(AVG(e.salary), 0)::NUMERIC(10,2) AS avg_salary,
    COALESCE(SUM(e.salary), 0) AS total_payroll,
    COALESCE(SUM(ep.hours_allocated), 0) AS project_hours,
    CASE 
        WHEN COUNT(e.id) = 0 THEN 'Empty'
        WHEN COUNT(e.id) < 3 THEN 'Small'
        WHEN COUNT(e.id) < 6 THEN 'Medium'
        ELSE 'Large'
    END AS size
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id
LEFT JOIN employee_projects ep ON e.id = ep.employee_id
GROUP BY d.id, d.name, d.location
ORDER BY employee_count DESC;
```

### Top Performers

```sql
SELECT 
    e.first_name || ' ' || e.last_name AS employee,
    COUNT(ep.project_id) AS project_count,
    SUM(ep.hours_allocated) AS total_hours
FROM employees e
JOIN employee_projects ep ON e.id = ep.employee_id
GROUP BY e.id, e.first_name, e.last_name
ORDER BY project_count DESC, total_hours DESC
LIMIT 5;
```

---
*Previous: 03 - SQL Fundamentals | Next: 05 - Constraints & Data Integrity*
