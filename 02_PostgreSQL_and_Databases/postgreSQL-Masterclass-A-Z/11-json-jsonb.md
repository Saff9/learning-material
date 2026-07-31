# 11 - JSON & JSONB: A Deep Dive

> The comprehensive masterclass on PostgreSQL's document database capabilities. Covering architecture, operators, advanced indexing strategies (GIN, RUM, pgvector), schema validation, and big data / cloud patterns.

---

## JSON vs JSONB Architecture

PostgreSQL offers two distinct data types for handling JSON, each with vastly different underlying mechanics and use cases. Understanding their architecture is key to performance.

| Feature | JSON | JSONB |
|---------|------|-------|
| Storage | Raw text (string) | Parsed binary (custom tree structure) |
| Whitespace | Preserved | Removed |
| Key order | Preserved | Not preserved (ordered by key length/alphabetically internally) |
| Duplicates | Kept | Last wins (deduplicated on insert) |
| Indexing | No native indexing | Yes (GIN, B-Tree, Hash, RUM) |
| Insert speed | Faster (no parsing overhead) | Slightly slower (parsing overhead) |
| Query speed | Slower (re-parsed on every read/function call) | Faster (binary traversal) |
| **Recommendation** | Use ONLY for logging or exact API passthroughs | **Default standard for 99% of use cases** |

### Under the Hood: TOAST and JSONB
When JSONB documents exceed the 8KB page size limit in Postgres, they are compressed and moved out-of-line to a **TOAST** (The Oversized-Attribute Storage Technique) table. 
- **Pro-tip:** Accessing a small key from a heavily TOASTed JSONB row can still be slow if the entire document needs decompression. Keep JSONB documents reasonably sized (under a few MBs) or normalize heavily queried scalar fields into standard relational columns.

---

## Creating and Modeling JSONB

```sql
-- From text (Implicit parsing)
SELECT '{"name": "Alice", "age": 30}'::JSONB;

-- Build object dynamically
SELECT jsonb_build_object('name', 'Alice', 'age', 30, 'tags', ARRAY['sql', 'db']);

-- Build array dynamically
SELECT jsonb_build_array('a', 'b', 'c');

-- From query (Aggregating relational data to JSON)
SELECT jsonb_object_agg(id, first_name) FROM employees;

-- Aggregate rows (N+1 query killer: fetch parents and children in one JSON structure)
SELECT jsonb_agg(
    jsonb_build_object(
        'id', id, 
        'name', first_name,
        'department', department_id
    )
) FROM employees;

-- Table Modeling Example
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO products (name, metadata) VALUES
    ('Laptop', '{"brand": "Dell", "specs": {"cpu": "i7", "ram": "16GB"}, "price": 1200}'),
    ('Phone', '{"brand": "Apple", "specs": {"model": "iPhone 16", "storage": "256GB"}, "price": 999}');
```

---

## Querying JSONB: Operators and SQL/JSON Path

### Extraction Operators

```sql
-- -> returns JSONB (Used for further chaining or returning objects)
SELECT metadata -> 'brand' FROM products;              -- "Dell" (JSONB string)
SELECT metadata -> 'specs' -> 'cpu' FROM products;     -- "i7"

-- ->> returns TEXT (Crucial for B-Tree indexing and casting)
SELECT (metadata ->> 'price')::numeric FROM products;  -- Cast to numeric

-- #> path (JSONB)
SELECT metadata #> '{specs,cpu}' FROM products;        -- "i7"

-- #>> path (TEXT)
SELECT metadata #>> '{specs,cpu}' FROM products;       -- i7

-- Array access (0-indexed, supports negative indices for end-relative access)
SELECT metadata -> 'tags' -> 0 FROM products;
SELECT metadata -> 'tags' -> -1 FROM products;         -- Last element
```

### Containment and Existence

```sql
-- @> contains (Is the right document a subset of the left document?)
-- The primary operator powered by GIN indexes!
SELECT * FROM products WHERE metadata @> '{"brand": "Dell"}';
SELECT * FROM products WHERE metadata @> '{"specs": {"cpu": "i7"}}';

-- <@ contained in
SELECT '{"cpu": "i7"}'::JSONB <@ (metadata -> 'specs') FROM products;

-- ? key exists at top level
SELECT * FROM products WHERE metadata ? 'price';

-- ?| any key exists (OR logic)
SELECT * FROM products WHERE metadata ?| ARRAY['color', 'warranty'];

-- ?& all keys exist (AND logic)
SELECT * FROM products WHERE metadata ?& ARRAY['brand', 'specs'];
```

### Modifying JSONB (Update Patterns)

```sql
-- || merge/update keys (Shallow merge)
UPDATE products SET metadata = metadata || '{"price": 999}'::JSONB;

-- - remove key (Text or Integer for array index)
UPDATE products SET metadata = metadata - 'warranty';

-- #- remove by path
UPDATE products SET metadata = metadata #- '{specs,ram}';

-- jsonb_set (Safe nested update. Signature: target, path, new_value, create_if_missing)
UPDATE products SET metadata = jsonb_set(
    metadata, '{specs,storage}', '"512GB"'::JSONB, true
);

-- jsonb_insert (into array)
UPDATE products SET metadata = jsonb_insert(
    metadata, '{tags,0}', '"new"'::JSONB
);
```

---

## JSONB Functions & Iteration

```sql
SELECT jsonb_each('{"a": 1, "b": 2}'::JSONB);           -- Expands to key-value pairs (set-returning)
SELECT jsonb_each_text('{"a": 1}'::JSONB);              -- Values as TEXT
SELECT jsonb_object_keys('{"a": 1}'::JSONB);            -- Keys only
SELECT * FROM jsonb_array_elements('[1, 2, 3]'::JSONB); -- Expand JSON array to rows
SELECT jsonb_array_length('[1, 2, 3]'::JSONB);          -- 3
SELECT jsonb_typeof('123'::JSONB);                      -- 'number', 'string', 'boolean', 'object', 'array', 'null'
SELECT jsonb_strip_nulls('{"a": 1, "b": null}'::JSONB); -- Recursively remove null values
```

---

## Advanced Indexing: B-Tree, GIN, RUM, and pgvector

Efficient querying of JSONB requires strategic indexing. Doing full-table scans on gigabytes of JSONB data will cripple performance.

### 1. B-Tree Indexes (Targeted Extraction)
Best for equality, ranges, and sorting on specific extracted scalars.
```sql
-- Index on specific nested key (Must use ->> to extract TEXT, or cast to correct type)
CREATE INDEX idx_products_brand ON products((metadata ->> 'brand'));
CREATE INDEX idx_products_price ON products(((metadata ->> 'price')::numeric));
```

### 2. GIN Indexes (General Inverted Index)
Best for searching inside dynamic schemas and unknown key structures (`@>`, `?`, `?&`).
```sql
-- Default GIN (Larger, indexes keys and values separately. Fast for existence `?`)
CREATE INDEX idx_products_metadata_default ON products USING gin(metadata);

-- jsonb_path_ops (Smaller, faster! Hashes paths. Only supports `@>` containment)
CREATE INDEX idx_products_metadata_path ON products USING gin(metadata jsonb_path_ops);
```

### 3. RUM Indexes (Advanced GIN)
An extension to Postgres (`pg_rum`), RUM indexes are designed for Full-Text Search inside JSONB and returning ranked results. If you need to search large JSON documents by text and sort by relevance, RUM is vastly superior to GIN.

### 4. Vector Search within JSON (pgvector)
With AI/ML workloads, you often store embeddings inside JSON payloads. `pgvector` allows hybrid searches combining JSON metadata filtering with vector similarity.
```sql
-- Example: Products table with vector embeddings inside JSONB
-- Note: It's heavily recommended to extract the vector to its own column for HNSW indexing.
ALTER TABLE products ADD COLUMN embedding vector(1536);

-- Update vector from JSON extraction
UPDATE products SET embedding = (metadata->>'vector_embedding')::vector;

-- Create HNSW Index on the vector column
CREATE INDEX idx_products_emb ON products USING hnsw (embedding vector_l2_ops);

-- Hybrid Search: Vector similarity + JSONB Metadata Filter
SELECT id, name, metadata->>'brand' as brand, embedding <-> '[0.1, 0.2, ...]' AS distance
FROM products
WHERE metadata @> '{"category": "electronics"}'
ORDER BY distance LIMIT 5;
```

---

## JSON Schema Validation

A common danger of NoSQL-in-SQL is schema decay. Postgres can enforce constraints on JSONB content to maintain data integrity.

### 1. Using CHECK Constraints
Ensure required keys and specific data types exist before insert.
```sql
ALTER TABLE products ADD CONSTRAINT check_metadata_schema 
CHECK (
    metadata ? 'brand' AND                           -- Brand must exist
    metadata ? 'specs' AND                           -- Specs must exist
    jsonb_typeof(metadata->'price') = 'number' AND   -- Price must be numeric
    (metadata->>'price')::numeric >= 0               -- Price cannot be negative
);
```

### 2. Full JSON Schema Extension
For complex applications, use the `postgres-json-schema` extension or native PL/pgSQL functions that implement Draft 7/2020-12 JSON Schema validation inside the database layer, rejecting non-conforming structures outright.

---

## Big Data & Cloud Patterns

### Hybrid Relational-Document Modeling
- **Do not put everything in JSONB!** If a field is queried frequently, joined on, or used for ordering/grouping, promote it to a standard relational column.
- Use JSONB for: Custom user attributes, 3rd party API payloads (webhooks), E-commerce product variants with diverse specifications, and feature toggles.
- **The "Data Lake" Pattern:** Write raw inbound data (IoT events, clickstreams) to an append-only JSONB table. Use Materialized Views or triggers to parse, extract, and normalize the critical data into relational tables asynchronously.

### Compression Thresholds
PostgreSQL compresses TOASTed data using PGLZ (or LZ4 in PG 14+). LZ4 is much faster. Set `default_toast_compression = 'lz4'` in your `postgresql.conf` for massive improvements on large JSONB datasets.

---

## JSON_TABLE and SQL/JSON Path (PostgreSQL 15+)

Standard SQL/JSON path language (`jsonpath`) allows for powerful querying and flattening.

```sql
-- jsonpath example: find products with RAM >= 16GB
SELECT * FROM products 
WHERE metadata @@ '$.specs.ram == "16GB"';

-- JSON_TABLE (Available heavily in PG17+, flattens arrays to rows)
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
