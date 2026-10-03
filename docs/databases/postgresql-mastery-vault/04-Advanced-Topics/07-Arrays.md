---
tags: [postgresql, advanced, arrays]
---

# Arrays

PostgreSQL can store arrays of any base type — useful for tags, lists, and denormalized data.

## Creating Array Columns

```sql
-- Using array syntax
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    tags TEXT[] NOT NULL DEFAULT '{}'
);

-- Using ARRAY keyword
INSERT INTO posts (title, tags) VALUES
    ('Post 1', ARRAY['postgres', 'sql', 'tutorial']),
    ('Post 2', ARRAY['python', 'web']),
    ('Post 3', '{postgres, performance}');  -- string literal syntax
```

## Querying Arrays

```sql
-- Check if value is in array (ANY)
SELECT * FROM posts WHERE 'postgres' = ANY(tags);

-- Check if value is in array (IN with unnest)
SELECT * FROM posts WHERE 'postgres' IN (SELECT unnest(tags));

-- Array overlap (&& — do they share any elements?)
SELECT * FROM posts WHERE tags && ARRAY['python', 'rust'];

-- Array contains (@> — does left contain all of right?)
SELECT * FROM posts WHERE tags @> ARRAY['postgres', 'sql'];

-- Array is contained by (<@ — is left a subset of right?)
SELECT * FROM posts WHERE tags <@ ARRAY['postgres', 'sql', 'tutorial'];
```

## Array Operations

```sql
-- Array length
SELECT title, array_length(tags, 1) AS tag_count FROM posts;

-- Expand array to rows (unnest)
SELECT title, unnest(tags) AS tag FROM posts;

-- Aggregate into array
SELECT department, array_agg(name ORDER BY salary DESC) AS employees
FROM employees GROUP BY department;

-- Concatenate arrays
SELECT ARRAY[1,2] || ARRAY[3,4];  -- {1,2,3,4}

-- Access element (1-indexed!)
SELECT tags[1] FROM posts;  -- first tag
```

## Indexing Arrays

```sql
-- GIN index for array containment queries
CREATE INDEX idx_posts_tags ON posts USING GIN (tags);

-- Now these queries use the index:
SELECT * FROM posts WHERE 'postgres' = ANY(tags);
SELECT * FROM posts WHERE tags @> ARRAY['postgres'];
```

## When to Use Arrays

> [!tip] Arrays vs separate tables
> Use arrays for:
> - Tags, categories (small, bounded lists)
> - Denormalized data for performance
> - When you never need to query "which posts have tag X" independently
>
> Use a separate junction table when:
> - You need to query the relationship independently
> - The list can grow large
> - You need metadata on the relationship (e.g., "who added this tag and when")

## Next

- [[04-Advanced-Topics/08-Stored-Procedures|Stored Procedures]]
- [[05-Administration/01-Users-Roles-Permissions|Users and Roles]]
