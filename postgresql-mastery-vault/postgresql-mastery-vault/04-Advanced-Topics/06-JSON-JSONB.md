---
tags: [postgresql, advanced, json, jsonb, document]
---

# JSON and JSONB

PostgreSQL's JSON support is one of its killer features. `jsonb` is the binary, indexable, preferred format.

## json vs jsonb

| Type | Storage | Indexing | Speed |
|------|---------|----------|-------|
| `json` | Original text | No | Slower queries |
| `jsonb` | Binary (decomposed) | Yes (GIN) | Faster queries |

> [!important] Always use jsonb
> Use `jsonb` for all new projects. It's faster, indexable, and supports more operators. Use `json` only when you need to preserve exact input formatting (whitespace, key order).

## Storing JSON

```sql
CREATE TABLE products (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    attributes JSONB NOT NULL DEFAULT '{}'
);

INSERT INTO products (name, attributes) VALUES
    ('Laptop', '{"color": "silver", "specs": {"ram": 16, "ssd": 512}, "tags": ["electronics", "portable"]}'),
    ('Phone', '{"color": "black", "specs": {"ram": 8, "storage": 128}, "tags": ["electronics", "mobile"]}');
```

## Querying JSON

```sql
-- Get a value as JSONB (->)
SELECT attributes->'color' FROM products;
-- Result: "silver" (with quotes — it's JSONB)

-- Get a value as TEXT (->>)
SELECT attributes->>'color' FROM products;
-- Result: silver (without quotes — it's text)

-- Navigate nested objects
SELECT attributes#>>'{specs,ram}' FROM products;
-- Result: 16 (text)

-- Access array elements
SELECT attributes->'tags'->0 FROM products;
-- Result: "electronics"
```

## Filtering with JSON

```sql
-- Equality on a key
SELECT * FROM products WHERE attributes->>'color' = 'silver';

-- Containment (does the JSON contain this structure?)
SELECT * FROM products WHERE attributes @> '{"color": "silver"}';

-- Key exists
SELECT * FROM products WHERE attributes ? 'color';

-- Any of these keys exist
SELECT * FROM products WHERE attributes ?| array['color', 'weight'];

-- All of these keys exist
SELECT * FROM products WHERE attributes ?& array['color', 'specs'];
```

## Indexing JSON

```sql
-- GIN index on the entire JSONB (supports @>, ?, ?|, ?&)
CREATE INDEX idx_products_attrs ON products USING GIN (attributes);

-- GIN index with jsonb_path_ops (smaller, only supports @>)
CREATE INDEX idx_products_attrs_path ON products USING GIN (attributes jsonb_path_ops);

-- Expression index on a specific key
CREATE INDEX idx_products_color ON products ((attributes->>'color'));
```

## Modifying JSON

```sql
-- Update a value
UPDATE products SET attributes = jsonb_set(attributes, '{color}', '"red"')
WHERE id = 1;

-- Add a new key
UPDATE products SET attributes = attributes || '{"weight": 1.5}'::jsonb WHERE id = 1;

-- Remove a key
UPDATE products SET attributes = attributes - 'weight' WHERE id = 1;

-- Append to an array
UPDATE products SET attributes = jsonb_set(
    attributes, '{tags}', attributes->'tags' || '"new_tag"'
) WHERE id = 1;
```

## JSON Path (SQL/JSON)

```sql
-- SQL/JSON path language (PostgreSQL 12+)
SELECT * FROM products
WHERE attributes @? '$.specs.ram ? (@ > 8)';

-- Extract with path
SELECT jsonb_path_query(attributes, '$.specs.*') FROM products WHERE id = 1;
```

## Practice

```sql
-- Create a table with JSONB and query it
CREATE TABLE events (id SERIAL PRIMARY KEY, data JSONB NOT NULL);
INSERT INTO events (data) VALUES
    ('{"type": "click", "user": "alice", "page": "/home"}'),
    ('{"type": "purchase", "user": "bob", "amount": 99.99}'),
    ('{"type": "click", "user": "alice", "page": "/products"}');

SELECT * FROM events WHERE data->>'type' = 'click';
SELECT data->>'user', COUNT(*) FROM events WHERE data->>'type' = 'click' GROUP BY data->>'user';
```

## Next

- [[04-Advanced-Topics/07-Arrays|Arrays]]
- [[04-Advanced-Topics/08-Stored-Procedures|Stored Procedures]]
