---
tags: [sql, fundamentals, select, beginner]
---

# SELECT Basics

The `SELECT` statement is the most common SQL command. It retrieves data from one or more tables.

## Basic SELECT

```sql
-- Select all columns
SELECT * FROM users;

-- Select specific columns (preferred — faster, clearer)
SELECT id, name, email FROM users;

-- Select with column aliases
SELECT name AS full_name, email AS contact FROM users;

-- Select with expressions
SELECT name, LENGTH(email) AS email_length FROM users;

-- Select with string concatenation
SELECT first_name || ' ' || last_name AS full_name FROM users;

-- Select with arithmetic
SELECT product_name, price, price * 1.18 AS price_with_tax FROM products;
```

## DISTINCT — Remove Duplicates

```sql
-- Get unique values
SELECT DISTINCT department FROM employees;

-- Multiple columns
SELECT DISTINCT department, job_title FROM employees;
```

## WHERE Clause — Filtering

See [[02-SQL-Fundamentals/02-FILTER-WHERE|FILTER and WHERE]] for the full guide.

```sql
SELECT * FROM users WHERE is_active = true;
SELECT * FROM products WHERE price > 100;
SELECT * FROM users WHERE created_at >= '2026-01-01';
SELECT * FROM products WHERE name LIKE 'Laptop%';
```

## ORDER BY — Sorting

```sql
-- Ascending (default)
SELECT * FROM users ORDER BY created_at;

-- Descending
SELECT * FROM users ORDER BY created_at DESC;

-- Multiple columns
SELECT * FROM employees ORDER BY department ASC, salary DESC;

-- By expression
SELECT * FROM products ORDER BY price * stock DESC;
```

## LIMIT and OFFSET — Pagination

```sql
-- First 10 rows
SELECT * FROM users ORDER BY created_at DESC LIMIT 10;

-- Page 2 (rows 11-20)
SELECT * FROM users ORDER BY created_at DESC LIMIT 10 OFFSET 10;

-- SQL-standard alternative
SELECT * FROM users ORDER BY created_at DESC FETCH FIRST 10 ROWS ONLY;
```

> [!warning] Always use ORDER BY with LIMIT
> Without `ORDER BY`, the order of rows is undefined. `LIMIT` without `ORDER BY` returns an unpredictable subset. Always pair them.

## Practice

```sql
-- Set up sample data
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT,
    salary NUMERIC(10,2),
    hire_date DATE
);

INSERT INTO employees (name, department, salary, hire_date) VALUES
    ('Alice', 'Engineering', 95000, '2020-03-15'),
    ('Bob', 'Engineering', 87000, '2019-07-01'),
    ('Carol', 'Sales', 72000, '2021-01-10'),
    ('Dave', 'Sales', 68000, '2022-05-20'),
    ('Eve', 'Marketing', 65000, '2023-02-14'),
    ('Frank', 'Engineering', 105000, '2018-11-03');

-- Try these queries:
SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 3;
SELECT DISTINCT department FROM employees;
SELECT name, salary, salary * 1.10 AS raise FROM employees WHERE department = 'Engineering';
```

## Next

- [[02-SQL-Fundamentals/02-FILTER-WHERE|FILTER and WHERE]]
- [[02-SQL-Fundamentals/03-ORDER-BY-LIMIT|ORDER BY and LIMIT]]
