---
tags: [sql, intermediate, views, virtual-tables]
---

# Views

Views are virtual tables based on a query. They simplify complex queries and provide a layer of abstraction.

## Creating Views

```sql
-- Simple view
CREATE VIEW active_users AS
SELECT id, name, email FROM users WHERE is_active = true;

-- Use it like a table
SELECT * FROM active_users;
SELECT name FROM active_users WHERE email LIKE '%@gmail.com';
```

## Complex Views

```sql
-- A view that joins and aggregates
CREATE VIEW user_summary AS
SELECT
    u.id,
    u.name,
    u.email,
    COUNT(o.id) AS order_count,
    COALESCE(SUM(o.amount), 0) AS total_spent,
    MAX(o.created_at) AS last_order_date
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.name, u.email;

-- Query the view
SELECT * FROM user_summary WHERE total_spent > 1000 ORDER BY total_spent DESC;
```

## Updatable Views

Simple views (single table, no aggregates) are automatically updatable:

```sql
CREATE VIEW active_users AS
SELECT id, name, email FROM users WHERE is_active = true;

-- This INSERT works (is_active defaults to true)
INSERT INTO active_users (name, email) VALUES ('New User', 'new@example.com');

-- This UPDATE works
UPDATE active_users SET name = 'Updated Name' WHERE id = 1;
```

## Managing Views

```sql
-- Replace a view
CREATE OR REPLACE VIEW active_users AS
SELECT id, name, email, created_at FROM users WHERE is_active = true;

-- Drop a view
DROP VIEW IF EXISTS active_users;

-- Rename
ALTER VIEW active_users RENAME TO current_users;
```

## When to Use Views

- **Simplify complex queries** — encapsulate joins and logic
- **Security** — expose only certain columns to certain users
- **Consistency** — ensure everyone uses the same query logic
- **Backward compatibility** — rename columns without breaking old queries

> [!warning] Views are not indexes
> Views do not store data (except materialized views). Every view query runs the underlying SQL. If the underlying query is slow, the view is slow.

## Next

- [[03-Intermediate-SQL/05-Materialized-Views|Materialized Views]]
- [[03-Intermediate-SQL/06-Indexes|Indexes]]
