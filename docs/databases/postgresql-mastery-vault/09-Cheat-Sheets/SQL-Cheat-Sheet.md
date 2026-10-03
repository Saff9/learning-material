---
tags: [cheat-sheet, sql, reference]
---

# SQL Cheat Sheet

## DDL (Data Definition)

```sql
CREATE DATABASE dbname;
CREATE TABLE name (col TYPE constraints);
ALTER TABLE name ADD COLUMN col TYPE;
ALTER TABLE name DROP COLUMN col;
ALTER TABLE name RENAME col TO new_col;
DROP TABLE name;
TRUNCATE TABLE name;  -- delete all rows, keep structure
```

## DML (Data Manipulation)

```sql
-- INSERT
INSERT INTO users (name, email) VALUES ('Alice', 'alice@x.com');
INSERT INTO users (name, email) VALUES ('Bob','b@x.com'), ('Carol','c@x.com');
INSERT INTO users SELECT * FROM temp_users;  -- from another table

-- UPDATE
UPDATE users SET name = 'Alice2' WHERE id = 1;
UPDATE users SET email = LOWER(email);  -- all rows

-- DELETE
DELETE FROM users WHERE id = 1;
DELETE FROM users;  -- all rows (no WHERE = everything)

-- UPSERT (INSERT ... ON CONFLICT)
INSERT INTO users (id, name) VALUES (1, 'Alice')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;
```

## DQL (Data Query)

```sql
SELECT col1, col2 FROM table
WHERE condition
GROUP BY col
HAVING count(*) > 1
ORDER BY col DESC
LIMIT 10 OFFSET 20;
```

## JOINs

```sql
SELECT * FROM a JOIN b ON a.id = b.a_id;        -- INNER
SELECT * FROM a LEFT JOIN b ON a.id = b.a_id;    -- all a, NULL b if no match
SELECT * FROM a RIGHT JOIN b ON a.id = b.a_id;   -- all b
SELECT * FROM a FULL JOIN b ON a.id = b.a_id;    -- all a and b
SELECT * FROM a CROSS JOIN b;                     -- Cartesian product
```

## Aggregates

```sql
COUNT(*), COUNT(col), COUNT(DISTINCT col)
SUM(col), AVG(col), MIN(col), MAX(col)
string_agg(col, ',' ORDER BY col)
array_agg(col ORDER BY col)
COUNT(*) FILTER (WHERE condition)  -- conditional count
```

## Window Functions

```sql
ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC)
RANK() OVER (ORDER BY score DESC)
DENSE_RANK() OVER (ORDER BY score DESC)
LAG(col, 1) OVER (ORDER BY date)
LEAD(col, 1) OVER (ORDER BY date)
SUM(col) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
```

## Common Patterns

```sql
-- Pagination
SELECT * FROM items ORDER BY id LIMIT 10 OFFSET 20;

-- Keyset pagination (faster for large offsets)
SELECT * FROM items WHERE id > 100 ORDER BY id LIMIT 10;

-- Find duplicates
SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;

-- Delete duplicates (keep one)
DELETE FROM users WHERE id NOT IN (
    SELECT MIN(id) FROM users GROUP BY email
);

-- Pivot
SELECT user_id,
    SUM(CASE WHEN month = 1 THEN amount ELSE 0 END) AS jan,
    SUM(CASE WHEN month = 2 THEN amount ELSE 0 END) AS feb
FROM orders GROUP BY user_id;
```

## Date/Time

```sql
NOW(), CURRENT_DATE, CURRENT_TIMESTAMP
date + INTERVAL '7 days'
EXTRACT(YEAR FROM date)
DATE_TRUNC('month', timestamp)
AGE(timestamp)  -- returns interval
```

## NULL Handling

```sql
IS NULL, IS NOT NULL
COALESCE(col, default)  -- first non-NULL value
NULLIF(a, b)  -- returns NULL if a = b
```

## Related

- [[09-Cheat-Sheets/psql-Commands|psql Commands]]
- [[09-Cheat-Sheets/Data-Types-Reference|Data Types Reference]]
- [[09-Cheat-Sheets/Common-Queries|Common Queries]]
