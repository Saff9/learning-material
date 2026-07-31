# 11 - JSON & JSONB

> Complete guide to PostgreSQL's document capabilities, operators, indexing, and patterns.

---

## JSON vs JSONB

| Feature | JSON | JSONB |
|---------|------|-------|
| Storage | Raw text | Parsed binary |
| Whitespace | Preserved | Removed |
| Key order | Preserved | Not preserved |
| Duplicates | Kept | Last wins |
| Indexing | No | Yes (GIN) |
| Insert speed | Faster | Slightly slower |
| Query speed | Slower | Faster |
| **Recommendation** | Rarely use | **Always use** |

---

## Creating JSONB

```sql
-- From text
SELECT '{"name": "Alice", "age": 30}'::JSONB;

-- Build object
SELECT jsonb_build_object('name', 'Alice', 'age', 30, 'tags', ARRAY['sql', 'db']);

-- Build array
SELECT jsonb_build_array('a', 'b', 'c');

-- From query
SELECT jsonb_object_agg(id, first_name) FROM employees;

-- Aggregate rows
SELECT jsonb_agg(jsonb_build_object('id', id, 'name', first_name)) FROM employees;

-- Create table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    metadata JSONB DEFAULT '{}'
);

INSERT INTO products (name, metadata) VALUES
    ('Laptop', '{"brand": "Dell", "specs": {"cpu": "i7", "ram": "16GB"}}'),
    ('Phone', '{"brand": "Apple", "specs": {"model": "iPhone 16", "storage": "256GB"}}');
```

---

## Querying JSONB

### Extraction Operators

```sql
-- -> returns JSONB
SELECT metadata -> 'brand' FROM products;              -- "Dell"
SELECT metadata -> 'specs' -> 'cpu' FROM products;     -- "i7"

-- ->> returns TEXT
SELECT metadata ->> 'brand' FROM products;             -- Dell

-- #> path (JSONB)
SELECT metadata #> '{specs,cpu}' FROM products;        -- "i7"

-- #>> path (TEXT)
SELECT metadata #>> '{specs,cpu}' FROM products;       -- i7

-- Array access
SELECT metadata -> 'tags' -> 0 FROM products;
```

### Containment

```sql
-- @> contains
SELECT * FROM products WHERE metadata @> '{"brand": "Dell"}';
SELECT * FROM products WHERE metadata @> '{"specs": {"cpu": "i7"}}';

-- <@ contained in
SELECT '{"cpu": "i7"}'::JSONB <@ (metadata -> 'specs') FROM products;

-- ? key exists
SELECT * FROM products WHERE metadata ? 'warranty';

-- ?| any key exists
SELECT * FROM products WHERE metadata ?| ARRAY['color', 'warranty'];

-- ?& all keys exist
SELECT * FROM products WHERE metadata ?& ARRAY['brand', 'specs'];
```

### Modifying JSONB

```sql
-- || merge/update keys
UPDATE products SET metadata = metadata || '{"price": 999}'::JSONB;

-- - remove key
UPDATE products SET metadata = metadata - 'warranty';

-- #- remove by path
UPDATE products SET metadata = metadata #- '{specs,ram}';

-- jsonb_set
UPDATE products SET metadata = jsonb_set(
    metadata, '{specs,storage}', '"512GB"'::JSONB
);

-- jsonb_insert (into array)
UPDATE products SET metadata = jsonb_insert(
    metadata, '{tags,0}', '"new"'::JSONB
);

-- jsonb_pretty
SELECT jsonb_pretty(metadata) FROM products;
```

---

## JSONB Functions

```sql
SELECT jsonb_each('{"a": 1, "b": 2}'::JSONB);        -- key-value pairs
SELECT jsonb_each_text('{"a": 1}'::JSONB);             -- values as text
SELECT jsonb_object_keys('{"a": 1}'::JSONB);           -- keys
SELECT * FROM jsonb_array_elements('[1, 2, 3]'::JSONB); -- expand array
SELECT jsonb_array_length('[1, 2, 3]'::JSONB);         -- 3
SELECT jsonb_typeof('123'::JSONB);                      -- number
SELECT jsonb_strip_nulls('{"a": 1, "b": null}'::JSONB); -- remove nulls
```

---

## Indexing JSONB

```sql
-- GIN index for containment/existence
CREATE INDEX idx_products_metadata ON products USING gin(metadata);

-- GIN with path ops (smaller, faster for @>)
CREATE INDEX idx_products_metadata_path ON products USING gin(metadata jsonb_path_ops);

-- B-tree on specific key
CREATE INDEX idx_products_brand ON products((metadata ->> 'brand'));

-- Index on nested key
CREATE INDEX idx_products_cpu ON products((metadata #>> '{specs,cpu}'));
```

---

## JSON_TABLE (PostgreSQL 17+)

```sql
-- Convert JSON to relational rows
SELECT * FROM JSON_TABLE(
    '[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]'::JSONB,
    '$[*]' COLUMNS (
        id INTEGER PATH '$.id',
        name TEXT PATH '$.name'
    )
) AS jt;
```

---
*Previous: 10 - Triggers | Next: 12 - Arrays & Composite Types*
