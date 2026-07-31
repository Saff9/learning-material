---
tags: [sql, intermediate, recursive, cte, hierarchical]
---

# Recursive Queries

Recursive CTEs allow you to query hierarchical or tree-structured data.

## Basic Recursive CTE

```sql
-- Org chart: find all subordinates of employee #1
WITH RECURSIVE subordinates AS (
    -- Anchor: start with the top manager
    SELECT id, name, manager_id, 1 AS level
    FROM employees
    WHERE id = 1

    UNION ALL

    -- Recursive: find direct reports of each person found so far
    SELECT e.id, e.name, e.manager_id, s.level + 1
    FROM employees e
    INNER JOIN subordinates s ON e.manager_id = s.id
)
SELECT id, name, level FROM subordinates ORDER BY level;
```

## How It Works

1. The **anchor** query runs first (finds the starting point)
2. The **recursive** member joins the anchor's output back to the table
3. This repeats until the recursive member returns no new rows
4. All results are combined with UNION ALL

## Tree Traversal Example

```sql
-- File system tree
CREATE TABLE folders (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id INTEGER REFERENCES folders(id)
);

INSERT INTO folders (name, parent_id) VALUES
    ('root', NULL),
    ('home', 1),
    ('user', 2),
    ('documents', 3),
    ('pictures', 3),
    ('downloads', 3);

-- Get full path of each folder
WITH RECURSIVE folder_tree AS (
    SELECT id, name, parent_id, name::TEXT AS path, 1 AS depth
    FROM folders WHERE parent_id IS NULL

    UNION ALL

    SELECT f.id, f.name, f.parent_id,
           ft.path || '/' || f.name AS path,
           ft.depth + 1
    FROM folders f
    JOIN folder_tree ft ON f.parent_id = ft.id
)
SELECT path, depth FROM folder_tree ORDER BY path;
-- Result:
-- root
-- root/home
-- root/home/user
-- root/home/user/documents
-- root/home/user/pictures
-- root/home/user/downloads
```

## Generating Series

```sql
-- Generate a series of dates
WITH RECURSIVE dates AS (
    SELECT DATE '2026-01-01' AS d
    UNION ALL
    SELECT d + 1 FROM dates WHERE d < '2026-01-31'
)
SELECT d FROM dates;

-- Or use generate_series (simpler)
SELECT generate_series(
    DATE '2026-01-01',
    DATE '2026-01-31',
    INTERVAL '1 day'
)::DATE AS d;
```

## Practice

```sql
-- Find the management chain for a specific employee (bottom-up)
WITH RECURSIVE management_chain AS (
    SELECT id, name, manager_id, 1 AS level
    FROM employees WHERE id = 5  -- start from employee #5

    UNION ALL

    SELECT e.id, e.name, e.manager_id, mc.level + 1
    FROM employees e
    JOIN management_chain mc ON mc.manager_id = e.id
)
SELECT name, level FROM management_chain ORDER BY level;
```

## Next

- [[03-Intermediate-SQL/04-Views|Views]]
- [[03-Intermediate-SQL/06-Indexes|Indexes]]
