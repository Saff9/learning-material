# 09 - JSON & JSONB

## JSON vs JSONB

PostgreSQL has two JSON types:

| Feature | JSON | JSONB |
|---------|------|-------|
| Storage | Text (preserves formatting) | Binary (parsed) |
| Whitespace | Preserved | Removed |
| Key order | Preserved | Not preserved |
| Duplicate keys | Kept (last wins) | Removed (last wins) |
| Indexing | Not indexable | Indexable with GIN |
| Performance | Faster to insert | Faster to query |
| **Recommendation** | Rarely use | **Always use** |

```sql
-- JSON preserves formatting
SELECT '{"name": "Alice", "age": 30}'::JSON;
-- Result: {"name": "Alice", "age": 30}  (exact text)

-- JSONB normalizes
SELECT '{"name": "Alice", "age": 30}'::JSONB;
-- Result: {"age": 30, "name": "Alice"}  (sorted, no extra spaces)
```

## Creating JSONB Data

```sql
-- From text
SELECT '{"name": "Alice", "skills": ["SQL", "Python"]}'::JSONB;

-- From row
SELECT row_to_json(employees) FROM employees WHERE id = 1;

-- Build JSONB object
SELECT jsonb_build_object(
    'name', 'Alice',
    'age', 30,
    'active', true,
    'salary', 75000.50
);

-- Build JSONB array
SELECT jsonb_build_array('SQL', 'Python', 'PostgreSQL');

-- Build from query
SELECT jsonb_object_agg(id, first_name) FROM employees;

-- Aggregating rows to JSONB
SELECT 
    jsonb_agg(
        jsonb_build_object(
            'id', id,
            'name', first_name || ' ' || last_name,
            'salary', salary
        )
    ) AS employees_json
FROM employees;

-- Create table with JSONB
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    metadata JSONB DEFAULT '{}'
);

INSERT INTO products (name, metadata) VALUES
    ('Laptop', '{"brand": "Dell", "specs": {"cpu": "i7", "ram": "16GB"}, "warranty": 2}'),
    ('Phone', '{"brand": "Apple", "specs": {"model": "iPhone 15", "storage": "256GB"}, "color": "black"}'),
    ('Monitor', '{"brand": "LG", "specs": {"size": "27"", "resolution": "4K"}, "ports": ["HDMI", "DisplayPort"]}');
```

## Querying JSONB

### Extraction Operators

```sql
-- ->  Returns JSONB (can chain)
SELECT metadata -> 'brand' FROM products;           -- "Dell" (JSONB string)
SELECT metadata -> 'specs' -> 'cpu' FROM products;  -- "i7"

-- ->> Returns TEXT (cannot chain)
SELECT metadata ->> 'brand' FROM products;            -- Dell (plain text)

-- #>  Path extraction (JSONB)
SELECT metadata #> '{specs,cpu}' FROM products;      -- "i7"

-- #>> Path extraction (TEXT)
SELECT metadata #>> '{specs,cpu}' FROM products;      -- i7

-- Array access
SELECT metadata -> 'ports' -> 0 FROM products WHERE id = 3;  -- "HDMI"
SELECT metadata -> 'ports' ->> 1 FROM products WHERE id = 3; -- DisplayPort
```

### Containment Operators

```sql
-- @>  Contains (left contains right)
SELECT * FROM products WHERE metadata @> '{"brand": "Dell"}';
SELECT * FROM products WHERE metadata @> '{"specs": {"cpu": "i7"}}';

-- <@  Contained in (right contains left)
SELECT '{"cpu": "i7"}'::JSONB <@ (metadata -> 'specs') FROM products;

-- ?   Key exists
SELECT * FROM products WHERE metadata ? 'warranty';

-- ?|  Any key exists
SELECT * FROM products WHERE metadata ?| ARRAY['color', 'warranty'];

-- ?&  All keys exist
SELECT * FROM products WHERE metadata ?& ARRAY['brand', 'specs'];
```

### Modifying JSONB

```sql
-- ||  Concatenate/merge (add or update keys)
UPDATE products 
SET metadata = metadata || '{"price": 999.99}'::JSONB 
WHERE id = 1;

-- -   Remove key
UPDATE products 
SET metadata = metadata - 'warranty' 
WHERE id = 1;

-- #-  Remove by path
UPDATE products 
SET metadata = metadata #- '{specs,ram}' 
WHERE id = 1;

-- jsonb_set: Update/create a specific path
UPDATE products 
SET metadata = jsonb_set(
    metadata, 
    '{specs,storage}', 
    '"512GB"'::JSONB
) 
WHERE id = 1;

-- jsonb_insert: Insert into array (without replacement)
UPDATE products 
SET metadata = jsonb_insert(
    metadata, 
    '{ports,1}', 
    '"USB-C"'::JSONB
) 
WHERE id = 3;

-- jsonb_pretty: Format for display
SELECT jsonb_pretty(metadata) FROM products WHERE id = 1;
```

### JSONB Functions

```sql
-- jsonb_each: Expand to key-value pairs
SELECT * FROM jsonb_each('{"a": 1, "b": 2}'::JSONB);
-- key | value
-- a   | 1
-- b   | 2

-- jsonb_each_text: Same but values as text
SELECT * FROM jsonb_each_text('{"a": 1, "b": "hello"}'::JSONB);

-- jsonb_object_keys: Get all keys
SELECT jsonb_object_keys('{"a": 1, "b": 2}'::JSONB);

-- jsonb_array_elements: Expand array to rows
SELECT * FROM jsonb_array_elements('[1, 2, 3]'::JSONB);

-- jsonb_array_elements_text: Same but text
SELECT * FROM jsonb_array_elements_text('["a", "b", "c"]'::JSONB);

-- jsonb_array_length: Array length
SELECT jsonb_array_length('[1, 2, 3, 4]'::JSONB);  -- 4

-- jsonb_typeof: Get type of JSONB value
SELECT jsonb_typeof('123'::JSONB);       -- number
SELECT jsonb_typeof('"hello"'::JSONB);  -- string
SELECT jsonb_typeof('true'::JSONB);     -- boolean
SELECT jsonb_typeof('[1,2]'::JSONB);    -- array
SELECT jsonb_typeof('{"a":1}'::JSONB);  -- object
SELECT jsonb_typeof('null'::JSONB);     -- null

-- jsonb_strip_nulls: Remove null values
SELECT jsonb_strip_nulls('{"a": 1, "b": null, "c": 3}'::JSONB);
-- {"a": 1, "c": 3}

-- jsonb_pretty: Pretty print
SELECT jsonb_pretty('{"name":"Alice","age":30}'::JSONB);
-- {
--     "name": "Alice",
--     "age": 30
-- }
```

## Indexing JSONB

```sql
-- GIN index for containment and existence queries
CREATE INDEX idx_products_metadata ON products USING gin(metadata);

-- GIN index with specific operator class
CREATE INDEX idx_products_metadata_gin ON products 
USING gin(metadata jsonb_path_ops);
-- jsonb_path_ops is smaller and faster for @> queries
-- But doesn't support ? and ?| operators

-- B-tree index on specific key (for equality/range)
CREATE INDEX idx_products_brand ON products((metadata ->> 'brand'));

-- Index on nested key
CREATE INDEX idx_products_cpu ON products((metadata #>> '{specs,cpu}'));

-- Partial index on JSONB
CREATE INDEX idx_products_with_warranty ON products(metadata) 
WHERE metadata ? 'warranty';

-- Multi-column index with JSONB
CREATE INDEX idx_products_name_brand ON products(name, (metadata ->> 'brand'));
```

## Practical Examples

### EAV (Entity-Attribute-Value) Alternative

```sql
-- Instead of EAV tables, use JSONB
CREATE TABLE entities (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50),
    attributes JSONB NOT NULL DEFAULT '{}'
);

INSERT INTO entities (entity_type, attributes) VALUES
    ('person', '{"name": "Alice", "age": 30, "email": "alice@example.com"}'),
    ('person', '{"name": "Bob", "age": 25, "phone": "555-0123"}'),
    ('product', '{"name": "Laptop", "price": 999, "category": "electronics"}'),
    ('product', '{"name": "Chair", "price": 199, "category": "furniture", "color": "brown"}');

-- Query all persons
SELECT * FROM entities 
WHERE entity_type = 'person' AND attributes @> '{"age": 30}';

-- Find products in price range
SELECT * FROM entities 
WHERE entity_type = 'product' 
  AND (attributes ->> 'price')::NUMERIC BETWEEN 100 AND 500;

-- Find entities with specific attribute
SELECT * FROM entities WHERE attributes ? 'email';
```

### Document Store Pattern

```sql
CREATE TABLE documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    collection VARCHAR(50),
    doc JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert document
INSERT INTO documents (collection, doc) VALUES
    ('users', '{"_id": "u1", "username": "alice", "profile": {"age": 30, "city": "NYC"}}'),
    ('users', '{"_id": "u2", "username": "bob", "profile": {"age": 25, "city": "LA"}}'),
    ('posts', '{"_id": "p1", "author": "u1", "title": "Hello", "tags": ["intro", "welcome"]}');

-- Find users in NYC
SELECT * FROM documents 
WHERE collection = 'users' AND doc @> '{"profile": {"city": "NYC"}}';

-- Find posts by author
SELECT * FROM documents 
WHERE collection = 'posts' AND doc @> '{"author": "u1"}';

-- Find documents with specific tag
SELECT * FROM documents 
WHERE collection = 'posts' AND doc -> 'tags' @> '["intro"]'::JSONB;

-- Full-text search on JSONB
SELECT * FROM documents 
WHERE to_tsvector('english', doc ->> 'title') @@ to_tsquery('hello');
```

### JSONB Aggregation

```sql
-- Build JSONB from relational data
SELECT 
    d.name AS department,
    jsonb_agg(
        jsonb_build_object(
            'id', e.id,
            'name', e.first_name || ' ' || e.last_name,
            'salary', e.salary
        ) ORDER BY e.salary DESC
    ) AS employees
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id
GROUP BY d.id, d.name;

-- Result:
-- department  | employees
-- Engineering | [{"id": 1, "name": "Alice Johnson", "salary": 95000}, ...]
-- Sales       | [{"id": 5, "name": "Eve Brown", "salary": 65000}, ...]
```

### Updating JSONB with Triggers

```sql
-- Auto-update JSONB audit trail
CREATE OR REPLACE FUNCTION update_jsonb_audit()
RETURNS TRIGGER AS $$
BEGIN
    NEW.metadata = jsonb_set(
        COALESCE(NEW.metadata, '{}'::JSONB),
        '{_audit}',
        jsonb_build_object(
            'updated_at', NOW(),
            'updated_by', current_user,
            'version', COALESCE((NEW.metadata -> '_audit' ->> 'version')::INT, 0) + 1
        )
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_products_audit
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_jsonb_audit();
```

## Summary

| Operator | Purpose |
|----------|---------|
| `->` | Extract JSONB field |
| `->>` | Extract text field |
| `#>` | Extract JSONB by path |
| `#>>` | Extract text by path |
| `@>` | Contains |
| `<@` | Is contained by |
| `?` | Key exists |
| `?\|` | Any key exists |
| `?&` | All keys exist |
| `\|\|` | Concatenate/merge |
| `-` | Remove key |
| `#-` | Remove by path |

| Function | Purpose |
|----------|---------|
| `jsonb_build_object()` | Build object from pairs |
| `jsonb_build_array()` | Build array |
| `jsonb_set()` | Update path |
| `jsonb_insert()` | Insert into array |
| `jsonb_pretty()` | Format output |
| `jsonb_each()` | Expand to rows |
| `jsonb_array_elements()` | Expand array to rows |
| `jsonb_object_keys()` | List keys |
| `jsonb_typeof()` | Get value type |
| `jsonb_strip_nulls()` | Remove null values |

---
*Previous: [08 - Functions & Triggers](08-functions-triggers.md) | Next: [10 - Views & Materialized Views](10-views-materialized-views.md)*
