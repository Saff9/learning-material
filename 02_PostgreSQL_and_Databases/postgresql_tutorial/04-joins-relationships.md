# 04 - Joins & Relationships

## Database Relationships

Relational databases are built on the concept of **relationships** between tables. Understanding how to model and query these relationships is fundamental.

### Types of Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                     ONE-TO-ONE                              │
│                                                             │
│   ┌──────────────┐         ┌──────────────┐               │
│   │   users      │         │ user_profiles│               │
│   │──────────────│         │──────────────│               │
│   │ id (PK)      │◄───────►│ user_id (FK) │               │
│   │ username     │         │ bio          │               │
│   │ email        │         │ avatar_url   │               │
│   └──────────────┘         └──────────────┘               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                     ONE-TO-MANY                             │
│                                                             │
│   ┌──────────────┐         ┌──────────────┐               │
│   │ departments  │         │  employees   │               │
│   │──────────────│         │──────────────│               │
│   │ id (PK)      │◄────────│ dept_id (FK) │               │
│   │ name         │    1:M  │ name         │               │
│   └──────────────┘         └──────────────┘               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                     MANY-TO-MANY                            │
│                                                             │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐│
│   │  students    │    │ enrollments  │    │   courses    ││
│   │──────────────│    │──────────────│    │──────────────││
│   │ id (PK)      │◄───│ student_id   │───►│ id (PK)      ││
│   │ name         │ M:M│ course_id    │ M:M│ title        ││
│   └──────────────┘    │ grade        │    └──────────────┘│
│                       └──────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

### Setting Up Example Tables

```sql
-- Departments (parent table)
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    budget DECIMAL(12, 2)
);

-- Employees (child table, one-to-many)
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    salary DECIMAL(10, 2) CHECK (salary > 0),
    hire_date DATE DEFAULT CURRENT_DATE,
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    manager_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Projects table
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    start_date DATE,
    end_date DATE,
    budget DECIMAL(12, 2)
);

-- Junction table for many-to-many (employees_projects)
CREATE TABLE employee_projects (
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    role VARCHAR(50),
    hours_allocated INTEGER,
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
    ('Alice', 'Johnson', 'alice@company.com', 95000, 1, NULL),    -- CEO, no manager
    ('Bob', 'Smith', 'bob@company.com', 80000, 1, 1),              -- Engineering manager
    ('Carol', 'Davis', 'carol@company.com', 75000, 1, 2),           -- Engineer
    ('David', 'Wilson', 'david@company.com', 72000, 1, 2),          -- Engineer
    ('Eve', 'Brown', 'eve@company.com', 65000, 2, 1),               -- Sales manager
    ('Frank', 'Miller', 'frank@company.com', 60000, 2, 5),          -- Sales rep
    ('Grace', 'Lee', 'grace@company.com', 58000, 2, 5),               -- Sales rep
    ('Henry', 'Taylor', 'henry@company.com', 70000, 3, 1),            -- Marketing manager
    ('Ivy', 'Anderson', 'ivy@company.com', 55000, 3, 8),              -- Marketing specialist
    ('Jack', 'Thomas', 'jack@company.com', 85000, 5, 1);               -- Finance manager

INSERT INTO projects (name, start_date, end_date, budget) VALUES
    ('Website Redesign', '2024-01-01', '2024-06-30', 50000),
    ('Mobile App', '2024-03-01', '2024-12-31', 120000),
    ('Data Migration', '2024-02-01', '2024-05-31', 30000),
    ('Cloud Migration', '2024-04-01', '2024-10-31', 200000);

INSERT INTO employee_projects (employee_id, project_id, role, hours_allocated) VALUES
    (2, 1, 'Tech Lead', 200),
    (3, 1, 'Developer', 300),
    (4, 1, 'Developer', 300),
    (2, 2, 'Tech Lead', 400),
    (3, 2, 'Developer', 500),
    (5, 3, 'Project Manager', 100),
    (8, 3, 'Coordinator', 150),
    (2, 4, 'Architect', 300),
    (10, 4, 'Financial Analyst', 200);
```

---

## JOIN Types

### INNER JOIN

Returns only rows where there is a match in **both** tables.

```sql
-- Employees with their departments
SELECT 
    e.first_name,
    e.last_name,
    e.salary,
    d.name AS department,
    d.location
FROM employees e
INNER JOIN departments d ON e.department_id = d.id;

-- Result: Only employees who have a department (no NULL department_id)
```

```
┌─────────────┬───────────┬─────────┬─────────────┬────────────┐
│ first_name  │ last_name │ salary  │ department  │ location   │
├─────────────┼───────────┼─────────┼─────────────┼────────────┤
│ Alice       │ Johnson   │ 95000   │ Engineering │ Building A │
│ Bob         │ Smith     │ 80000   │ Engineering │ Building A │
│ Carol       │ Davis     │ 75000   │ Engineering │ Building A │
│ ...         │ ...       │ ...     │ ...         │ ...        │
└─────────────┴───────────┴─────────┴─────────────┴────────────┘
```

### LEFT JOIN (LEFT OUTER JOIN)

Returns **all** rows from the left table, and matched rows from the right. Unmatched right rows show NULL.

```sql
-- All employees, with department info if available
SELECT 
    e.first_name,
    e.last_name,
    COALESCE(d.name, 'No Department') AS department
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id;

-- Employees without a department
SELECT e.first_name, e.last_name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id
WHERE d.id IS NULL;

-- All departments and their employees (some departments may have no employees)
SELECT 
    d.name AS department,
    e.first_name,
    e.last_name
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id
ORDER BY d.name;
```

### RIGHT JOIN (RIGHT OUTER JOIN)

Returns **all** rows from the right table, and matched rows from the left. Unmatched left rows show NULL.

```sql
-- Same as above but reversed
SELECT 
    d.name AS department,
    e.first_name,
    e.last_name
FROM employees e
RIGHT JOIN departments d ON e.department_id = d.id;

-- Note: RIGHT JOIN is rarely used; just swap table order and use LEFT JOIN
```

### FULL JOIN (FULL OUTER JOIN)

Returns **all** rows from both tables. Unmatched rows show NULL on the opposite side.

```sql
-- All employees and all departments, matched where possible
SELECT 
    e.first_name,
    e.last_name,
    d.name AS department
FROM employees e
FULL JOIN departments d ON e.department_id = d.id;

-- Find employees without departments AND departments without employees
SELECT 
    e.first_name,
    e.last_name,
    d.name AS department
FROM employees e
FULL JOIN departments d ON e.department_id = d.id
WHERE e.id IS NULL OR d.id IS NULL;
```

### CROSS JOIN

Returns the **Cartesian product** — every row from the first table combined with every row from the second.

```sql
-- All possible employee-department combinations
SELECT e.first_name, d.name AS department
FROM employees e
CROSS JOIN departments d;
-- Result: 10 employees × 5 departments = 50 rows

-- Equivalent syntax (implicit cross join)
SELECT e.first_name, d.name AS department
FROM employees e, departments d;
```

### SELF JOIN

A table joined to itself. Useful for hierarchical data.

```sql
-- Employee and their manager
SELECT 
    e.first_name AS employee_name,
    e.last_name AS employee_last,
    m.first_name AS manager_name,
    m.last_name AS manager_last
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;

-- Result:
┌──────────────┬───────────────┬──────────────┬───────────────┐
│ employee_name│ employee_last │ manager_name │ manager_last  │
├──────────────┼───────────────┼──────────────┼───────────────┤
│ Alice        │ Johnson       │ NULL         │ NULL          │  -- CEO
│ Bob          │ Smith         │ Alice        │ Johnson       │
│ Carol        │ Davis         │ Bob          │ Smith         │
│ ...          │ ...           │ ...          │ ...           │
└──────────────┴───────────────┴──────────────┴───────────────┘

-- Employees who earn more than their managers
SELECT 
    e.first_name || ' ' || e.last_name AS employee,
    e.salary AS emp_salary,
    m.first_name || ' ' || m.last_name AS manager,
    m.salary AS mgr_salary
FROM employees e
JOIN employees m ON e.manager_id = m.id
WHERE e.salary > m.salary;

-- Find all subordinates of a manager (recursive - see CTEs)
```

---

## Multiple JOINs

```sql
-- Employees with departments and managers
SELECT 
    e.id,
    e.first_name || ' ' || e.last_name AS employee,
    d.name AS department,
    d.location,
    m.first_name || ' ' || m.last_name AS manager
FROM employees e
INNER JOIN departments d ON e.department_id = d.id
LEFT JOIN employees m ON e.manager_id = m.id;

-- Employees, their departments, and their projects
SELECT 
    e.first_name || ' ' || e.last_name AS employee,
    d.name AS department,
    p.name AS project,
    ep.role,
    ep.hours_allocated
FROM employees e
INNER JOIN departments d ON e.department_id = d.id
LEFT JOIN employee_projects ep ON e.id = ep.employee_id
LEFT JOIN projects p ON ep.project_id = p.id
ORDER BY e.last_name, p.name;

-- Find departments with total project hours
SELECT 
    d.name AS department,
    COUNT(DISTINCT e.id) AS employee_count,
    COALESCE(SUM(ep.hours_allocated), 0) AS total_hours
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id
LEFT JOIN employee_projects ep ON e.id = ep.employee_id
GROUP BY d.id, d.name
ORDER BY total_hours DESC;
```

---

## JOIN Visual Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                      JOIN TYPE VISUALIZATION                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Table A          Table B          INNER JOIN (A ∩ B)           │
│  ┌──────┐        ┌──────┐         ┌──────────────┐              │
│  │  ●   │   ●    │  ●   │         │  ● (matched) │              │
│  │  ●   │   ●    │  ○   │         │  ● (matched) │              │
│  │  ○   │   ●    │  ●   │         └──────────────┘              │
│  └──────┘        └──────┘                                       │
│                                                                  │
│  LEFT JOIN (A)                   RIGHT JOIN (B)                  │
│  ┌──────────────┐               ┌──────────────┐                 │
│  │  ● (matched) │               │  ● (matched) │                 │
│  │  ● (matched) │               │  ○ (NULL)    │                 │
│  │  ○ (NULL)    │               │  ● (matched) │                 │
│  └──────────────┘               └──────────────┘                 │
│                                                                  │
│  FULL JOIN (A ∪ B)                                              │
│  ┌──────────────┐                                               │
│  │  ● (matched) │                                               │
│  │  ● (matched) │                                               │
│  │  ○ (NULL A)  │                                               │
│  │  ○ (NULL B)  │                                               │
│  └──────────────┘                                               │
│                                                                  │
│  CROSS JOIN (A × B)                                             │
│  All combinations of A and B rows                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Referential Integrity with Foreign Keys

### ON DELETE Actions

```sql
-- CASCADE: Delete child rows when parent is deleted
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE
);
-- If customer is deleted, all their orders are deleted

-- SET NULL: Set foreign key to NULL when parent is deleted
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL
);
-- If department is deleted, employees' department_id becomes NULL

-- SET DEFAULT: Set to default value
CREATE TABLE employees (
    department_id INTEGER DEFAULT 1 REFERENCES departments(id) ON DELETE SET DEFAULT
);

-- RESTRICT: Prevent deletion of parent if children exist
CREATE TABLE employees (
    department_id INTEGER REFERENCES departments(id) ON DELETE RESTRICT
);
-- Cannot delete department if employees reference it

-- NO ACTION: Same as RESTRICT but checked at end of transaction
CREATE TABLE employees (
    department_id INTEGER REFERENCES departments(id) ON DELETE NO ACTION
);
```

### ON UPDATE Actions

```sql
-- CASCADE: Update child foreign keys when parent PK changes
CREATE TABLE employees (
    department_id INTEGER REFERENCES departments(id) ON UPDATE CASCADE
);
-- If department.id changes, employee.department_id updates automatically

-- All the same options apply: CASCADE, SET NULL, SET DEFAULT, RESTRICT, NO ACTION
```

### Deferred Constraints

```sql
-- Normally, foreign keys are checked immediately
-- Deferred constraints check at transaction commit

CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    parent_id INTEGER REFERENCES accounts(id) DEFERRABLE INITIALLY DEFERRED
);

-- This allows circular references within a transaction:
BEGIN;
INSERT INTO accounts (id, name, parent_id) VALUES (1, 'Root', 2);
INSERT INTO accounts (id, name, parent_id) VALUES (2, 'Child', 1);
COMMIT;  -- Constraint checked here, both rows exist
```

---

## Practical Examples

### Finding Top Performers

```sql
-- Employees working on the most projects
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

### Department Statistics

```sql
-- Comprehensive department report
SELECT 
    d.name AS department,
    d.location,
    d.budget,
    COUNT(e.id) AS employee_count,
    COALESCE(AVG(e.salary), 0) AS avg_salary,
    COALESCE(SUM(e.salary), 0) AS total_payroll,
    COALESCE(SUM(ep.hours_allocated), 0) AS project_hours,
    CASE 
        WHEN COUNT(e.id) = 0 THEN 'Empty'
        WHEN COUNT(e.id) < 3 THEN 'Small'
        WHEN COUNT(e.id) < 6 THEN 'Medium'
        ELSE 'Large'
    END AS size_category
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id
LEFT JOIN employee_projects ep ON e.id = ep.employee_id
GROUP BY d.id, d.name, d.location, d.budget
ORDER BY employee_count DESC;
```

### Project Resource Allocation

```sql
-- Who is over-allocated (more than 500 hours)
SELECT 
    e.first_name || ' ' || e.last_name AS employee,
    d.name AS department,
    STRING_AGG(DISTINCT p.name, ', ') AS projects,
    SUM(ep.hours_allocated) AS total_allocated_hours
FROM employees e
JOIN departments d ON e.department_id = d.id
JOIN employee_projects ep ON e.id = ep.employee_id
JOIN projects p ON ep.project_id = p.id
GROUP BY e.id, e.first_name, e.last_name, d.name
HAVING SUM(ep.hours_allocated) > 500
ORDER BY total_allocated_hours DESC;
```

---

## Summary

| Join Type | Returns |
|-----------|---------|
| `INNER JOIN` | Only matching rows from both tables |
| `LEFT JOIN` | All left rows + matched right rows (NULL for unmatched) |
| `RIGHT JOIN` | All right rows + matched left rows (NULL for unmatched) |
| `FULL JOIN` | All rows from both tables (NULL where no match) |
| `CROSS JOIN` | Cartesian product of both tables |
| `SELF JOIN` | Table joined to itself |

You now understand:
- One-to-one, one-to-many, and many-to-many relationships
- All JOIN types and when to use each
- Referential integrity with ON DELETE/UPDATE actions
- Deferred constraints
- Complex multi-table queries

---
*Previous: [03 - SQL Fundamentals](03-sql-fundamentals.md) | Next: [05 - Constraints & Indexes](05-constraints-indexes.md)*
