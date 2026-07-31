---
tags: [sql, fundamentals, joins]
---

# JOINs

JOINs combine rows from two or more tables based on a related column. This is one of the most important SQL concepts.

## Types of JOINs

```
INNER JOIN:     only matching rows from both tables
LEFT JOIN:      all rows from left, NULLs if no match in right
RIGHT JOIN:     all rows from right, NULLs if no match in left
FULL JOIN:      all rows from both, NULLs where no match
CROSS JOIN:     Cartesian product (every combination)
SELF JOIN:      join a table to itself
```

## INNER JOIN (Most Common)

```sql
-- Get employees with their department names
SELECT e.name, e.salary, d.department_name
FROM employees e
INNER JOIN departments d ON e.department_id = d.id;

-- Shorter syntax (INNER is optional)
SELECT e.name, d.department_name
FROM employees e
JOIN departments d ON e.department_id = d.id;

-- Using USING (when column names match)
SELECT e.name, d.department_name
FROM employees e
JOIN departments d USING (department_id);
```

## LEFT JOIN

```sql
-- All employees, even those without a department
SELECT e.name, d.department_name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id;
-- If employee has no department, department_name will be NULL

-- Find employees WITHOUT a department
SELECT e.name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id
WHERE d.id IS NULL;
```

## RIGHT JOIN

```sql
-- All departments, even those with no employees
SELECT e.name, d.department_name
FROM employees e
RIGHT JOIN departments d ON e.department_id = d.id;
-- If department has no employees, name will be NULL
```

## FULL OUTER JOIN

```sql
-- All employees and all departments, matched where possible
SELECT e.name, d.department_name
FROM employees e
FULL OUTER JOIN departments d ON e.department_id = d.id;
```

## CROSS JOIN

```sql
-- Every employee paired with every project (Cartesian product)
-- Be careful — this can produce a LOT of rows!
SELECT e.name, p.project_name
FROM employees e
CROSS JOIN projects p;
```

## Multiple JOINs

```sql
-- Join 3 tables: users, posts, comments
SELECT
    u.name AS author,
    p.title AS post_title,
    c.body AS comment
FROM users u
JOIN posts p ON p.user_id = u.id
JOIN comments c ON c.post_id = p.id
ORDER BY p.created_at DESC, c.created_at;
```

## SELF JOIN

```sql
-- Employee and their manager (both in the same table)
SELECT
    e.name AS employee,
    m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;

-- Find all pairs of employees in the same department
SELECT a.name, b.name, a.department
FROM employees a
JOIN employees b ON a.department = b.department AND a.id < b.id;
```

## JOIN with Aggregates

```sql
-- Count posts per user
SELECT u.name, COUNT(p.id) AS post_count
FROM users u
LEFT JOIN posts p ON p.user_id = u.id
GROUP BY u.name
ORDER BY post_count DESC;

-- Total revenue per customer
SELECT c.name, SUM(o.amount) AS total_spent
FROM customers c
JOIN orders o ON o.customer_id = c.id
GROUP BY c.name
ORDER BY total_spent DESC;
```

## JOIN Performance Tips

> [!tip] Index foreign key columns
> PostgreSQL does NOT automatically create indexes on foreign key columns. Always index them for JOIN performance:
> ```sql
> CREATE INDEX idx_posts_user_id ON posts(user_id);
> CREATE INDEX idx_comments_post_id ON comments(post_id);
> ```

```sql
-- Use EXPLAIN to verify JOINs use indexes
EXPLAIN SELECT * FROM posts p JOIN comments c ON c.post_id = p.id WHERE p.id = 42;
```

## Practice

```sql
-- Set up sample data
CREATE TABLE departments (id SERIAL PRIMARY KEY, name TEXT);
INSERT INTO departments (name) VALUES ('Engineering'), ('Sales'), ('Marketing'), ('HR');

-- Add department_id to employees
ALTER TABLE employees ADD COLUMN department_id INTEGER REFERENCES departments(id);
UPDATE employees SET department_id = 1 WHERE department = 'Engineering';
UPDATE employees SET department_id = 2 WHERE department = 'Sales';
UPDATE employees SET department_id = 3 WHERE department = 'Marketing';

-- Try these JOINs:
SELECT e.name, d.name AS dept
FROM employees e
JOIN departments d ON e.department_id = d.id;

SELECT d.name AS dept, COUNT(e.id) AS emp_count
FROM departments d
LEFT JOIN employees e ON e.department_id = d.id
GROUP BY d.name
ORDER BY emp_count DESC;
```

## Next

- [[02-SQL-Fundamentals/07-Subqueries|Subqueries]]
- [[02-SQL-Fundamentals/08-Set-Operations|Set Operations]]
