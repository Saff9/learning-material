---
tags: [sql, fundamentals, subqueries]
---

# Subqueries

A subquery is a query inside another query. They are useful for complex filtering and data retrieval.

## Non-Correlated Subqueries

The subquery runs once and returns a value that the outer query uses.

```sql
-- Employees earning more than the average salary
SELECT name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);

-- Products more expensive than average in their category
SELECT name, price
FROM products
WHERE price > (SELECT AVG(price) FROM products WHERE category = 'electronics')
AND category = 'electronics';

-- Users who have placed orders
SELECT name FROM users
WHERE id IN (SELECT user_id FROM orders);

-- Users who have NOT placed orders
SELECT name FROM users
WHERE id NOT IN (SELECT user_id FROM orders WHERE user_id IS NOT NULL);
```

## Correlated Subqueries

The subquery references the outer query and runs once per outer row.

```sql
-- Employees earning more than their department's average
SELECT e.name, e.salary, e.department
FROM employees e
WHERE e.salary > (
    SELECT AVG(e2.salary)
    FROM employees e2
    WHERE e2.department = e.department
);

-- Count of posts for each user (in SELECT clause)
SELECT
    u.name,
    (SELECT COUNT(*) FROM posts p WHERE p.user_id = u.id) AS post_count
FROM users u;
```

> [!note] Correlated vs Non-Correlated
> Non-correlated subqueries run once. Correlated subqueries run once per outer row (potentially slow). For correlated subqueries, consider rewriting as JOINs for performance.

## Subquery in FROM (Derived Tables)

```sql
-- Use a subquery as a table
SELECT department, avg_salary
FROM (
    SELECT department, AVG(salary) AS avg_salary
    FROM employees
    GROUP BY department
) dept_stats
WHERE avg_salary > 70000;

-- With a column alias
SELECT t.name, t.total
FROM (
    SELECT user_id, COUNT(*) AS total
    FROM orders
    GROUP BY user_id
) t
WHERE t.total > 10;
```

## EXISTS

```sql
-- Users who have at least one order (EXISTS is often faster than IN)
SELECT name FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);

-- Users who have NO orders
SELECT name FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);
```

> [!tip] Use EXISTS over IN for large datasets
> `EXISTS` stops scanning as soon as it finds a match. `IN` scans the entire subquery. For large subquery results, `EXISTS` is often faster.

## Subquery vs JOIN

Most subqueries can be rewritten as JOINs, and vice versa. Use whichever is clearer:

```sql
-- Subquery approach
SELECT name FROM users
WHERE id IN (SELECT user_id FROM orders);

-- JOIN approach (same result, often faster)
SELECT DISTINCT u.name
FROM users u
JOIN orders o ON o.user_id = u.id;
```

## Practice

```sql
-- Find the highest-paid employee
SELECT name, salary FROM employees
WHERE salary = (SELECT MAX(salary) FROM employees);

-- Find departments where everyone earns more than 50000
SELECT department FROM employees e
GROUP BY department
HAVING MIN(salary) > 50000;

-- Find employees who earn more than the company average
-- AND more than their department average
SELECT name, salary, department
FROM employees e
WHERE salary > (SELECT AVG(salary) FROM employees)
  AND salary > (SELECT AVG(salary) FROM employees WHERE department = e.department);
```

## Next

- [[02-SQL-Fundamentals/08-Set-Operations|Set Operations]]
- [[03-Intermediate-SQL/01-Window-Functions|Window Functions]]
