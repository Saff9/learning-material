---
tags: [sql, fundamentals, where, filter, beginner]
---

# FILTER and WHERE

The `WHERE` clause filters rows before they are grouped or returned. It is one of the most important SQL concepts.

## Comparison Operators

```sql
-- Equal
SELECT * FROM users WHERE department = 'Engineering';

-- Not equal (!= or <>)
SELECT * FROM users WHERE department != 'Sales';

-- Greater than / less than
SELECT * FROM products WHERE price > 100;
SELECT * FROM products WHERE stock < 10;

-- Greater/less than or equal
SELECT * FROM employees WHERE salary >= 80000;
```

## Logical Operators (AND, OR, NOT)

```sql
-- AND: both conditions must be true
SELECT * FROM employees
WHERE department = 'Engineering' AND salary > 90000;

-- OR: either condition must be true
SELECT * FROM employees
WHERE department = 'Sales' OR department = 'Marketing';

-- NOT: negates a condition
SELECT * FROM employees
WHERE NOT department = 'Engineering';

-- Combine with parentheses
SELECT * FROM employees
WHERE (department = 'Engineering' OR department = 'Sales')
  AND salary > 70000;
```

## BETWEEN

```sql
-- Inclusive range
SELECT * FROM products WHERE price BETWEEN 100 AND 500;
-- Equivalent to: price >= 100 AND price <= 500

-- NOT BETWEEN
SELECT * FROM products WHERE price NOT BETWEEN 100 AND 500;

-- Dates
SELECT * FROM orders WHERE created_at BETWEEN '2026-01-01' AND '2026-12-31';
```

## IN

```sql
-- Match any value in a list
SELECT * FROM employees WHERE department IN ('Engineering', 'Sales', 'Marketing');

-- NOT IN
SELECT * FROM employees WHERE department NOT IN ('Engineering', 'Sales');

-- With subquery
SELECT * FROM products WHERE category_id IN (SELECT id FROM categories WHERE is_active = true);
```

## LIKE and ILIKE — Pattern Matching

```sql
-- LIKE: case-sensitive
SELECT * FROM users WHERE name LIKE 'Ali%';      -- starts with "Ali"
SELECT * FROM users WHERE name LIKE '%son';      -- ends with "son"
SELECT * FROM users WHERE name LIKE '%a%';       -- contains "a"
SELECT * FROM users WHERE name LIKE '_lice';     -- second char is "l", "Alice" matches

-- ILIKE: case-insensitive (PostgreSQL-specific)
SELECT * FROM users WHERE name ILIKE 'ali%';     -- matches "Alice", "alice", "ALICE"

-- Wildcards:
-- % = zero or more characters
-- _ = exactly one character
```

> [!tip] Use pg_trgm for better fuzzy search
> For real fuzzy search (typos, similarity), install the `pg_trgm` extension and use the `%` operator. See [[06-Extensions/03-pg_trgm|pg_trgm]].

## IS NULL / IS NOT NULL

```sql
-- NULL means "unknown" or "not set"
SELECT * FROM users WHERE email IS NULL;
SELECT * FROM users WHERE email IS NOT NULL;

-- Never use = NULL (it always returns NULL, not true)
-- WRONG: SELECT * FROM users WHERE email = NULL;
-- RIGHT: SELECT * FROM users WHERE email IS NULL;
```

## Date/Time Filtering

```sql
-- Today
SELECT * FROM events WHERE event_date = CURRENT_DATE;

-- Last 7 days
SELECT * FROM events WHERE created_at >= NOW() - INTERVAL '7 days';

-- Specific date range
SELECT * FROM orders
WHERE created_at >= '2026-01-01' AND created_at < '2026-02-01';

-- Extract parts of a date
SELECT * FROM orders WHERE EXTRACT(YEAR FROM created_at) = 2026;
SELECT * FROM orders WHERE EXTRACT(MONTH FROM created_at) = 7;
SELECT * FROM orders WHERE DATE(created_at) = '2026-07-15';
```

## JSON/JSONB Filtering

```sql
-- Filter on JSON data
SELECT * FROM products WHERE attributes->>'color' = 'red';
SELECT * FROM products WHERE attributes @> '{"color": "red"}';
SELECT * FROM products WHERE attributes->'price' > 100;
```

## Array Filtering

```sql
-- Check if value is in array
SELECT * FROM posts WHERE 'postgres' = ANY(tags);
SELECT * FROM posts WHERE 'postgres' IN (SELECT unnest(tags));

-- Array overlap
SELECT * FROM posts WHERE tags && ARRAY['postgres', 'sql'];

-- Array contains
SELECT * FROM posts WHERE tags @> ARRAY['postgres', 'sql'];
```

## Regular Expressions

PostgreSQL supports POSIX regular expressions with `~` (case-sensitive) and `~*` (case-insensitive).

```sql
-- Matches a pattern
SELECT * FROM users WHERE email ~ '^[a-z]+@[a-z]+\.[a-z]+$';

-- Case-insensitive
SELECT * FROM users WHERE name ~* '^ali';

-- Does NOT match
SELECT * FROM users WHERE email !~ '@gmail\.com$';
```

## Practice

```sql
-- Try these on the employees table from the previous section
SELECT * FROM employees WHERE salary BETWEEN 70000 AND 90000;
SELECT * FROM employees WHERE department IN ('Engineering', 'Marketing');
SELECT * FROM employees WHERE name ILIKE '%a%';
SELECT * FROM employees WHERE hire_date >= '2020-01-01' AND salary > 70000;
```

## Next

- [[02-SQL-Fundamentals/03-ORDER-BY-LIMIT|ORDER BY and LIMIT]]
- [[02-SQL-Fundamentals/04-Aggregate-Functions|Aggregate Functions]]
