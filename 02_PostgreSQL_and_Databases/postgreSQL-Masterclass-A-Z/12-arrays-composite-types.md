# 12 - Arrays, Composite Types & Specialized Data

> Arrays, composite types, ranges, network types, geometric types, UUID, Domain Types, PostGIS, and pgvector.

PostgreSQL goes far beyond standard relational modeling, offering robust support for advanced data types that handle complex application needs directly in the database. This guide explores these types, diving deep into their internal architectures, indexing strategies, real-world edge cases, and best practices.

---

## Arrays

PostgreSQL allows columns of a table to be defined as variable-length multidimensional arrays. Arrays can be of any built-in or user-defined base type, enum type, composite type, range type, or domain.

```sql
CREATE TABLE blog_posts (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    tags TEXT[] DEFAULT '{}',
    scores INTEGER[] DEFAULT '{}',
    matrix NUMERIC[][]  -- 2D array
);

-- Insert arrays
INSERT INTO blog_posts (title, tags, scores)
VALUES ('PostgreSQL Guide', ARRAY['sql', 'database', 'tutorial'], ARRAY[5, 4, 5]);

-- Array literals (curly brace syntax)
INSERT INTO blog_posts (title, tags)
VALUES ('Advanced SQL', '{advanced,sql,optimization}');

-- Access elements
SELECT tags[1] FROM blog_posts;           -- First element (PostgreSQL arrays are 1-indexed!)
SELECT tags[1:2] FROM blog_posts;         -- Slice: returns an array of the first two elements
```

### Advanced Array Operations & Edge Cases

```sql
-- Array operations
SELECT * FROM blog_posts WHERE tags @> ARRAY['sql'];        -- Contains: tags has 'sql'
SELECT * FROM blog_posts WHERE tags <@ ARRAY['sql','db'];   -- Contained in: tags only contains 'sql' or 'db'
SELECT * FROM blog_posts WHERE tags && ARRAY['sql'];        -- Overlap: tags has at least one common element
SELECT * FROM blog_posts WHERE 'sql' = ANY(tags);           -- Any element matches
SELECT * FROM blog_posts WHERE ARRAY['sql','db'] = ALL(tags); -- All elements match

-- Array functions
SELECT array_length(tags, 1) FROM blog_posts;       -- Dimension length
SELECT array_dims(tags) FROM blog_posts;            -- Dimensions string, e.g., '[1:3]'
SELECT array_append(tags, 'new') FROM blog_posts;   -- Add element to end
SELECT array_prepend('new', tags) FROM blog_posts;  -- Add element to beginning
SELECT array_remove(tags, 'sql') FROM blog_posts;   -- Remove all occurrences of value
SELECT array_position(tags, 'sql') FROM blog_posts; -- Find position (1-indexed)
SELECT array_distinct(tags) FROM blog_posts;        -- Unique values (PostgreSQL 14+)
SELECT array_sort(tags) FROM blog_posts;            -- Sort elements (PostgreSQL 14+)
SELECT array_agg(title ORDER BY id) FROM blog_posts; -- Aggregate rows into an array
SELECT unnest(tags) FROM blog_posts;                -- Expand array elements to multiple rows

-- Multidimensional constraints (Arrays must be rectangular)
-- INSERT INTO blog_posts (matrix) VALUES ('{{1,2}, {3}}'); -- ERROR: multidimensional arrays must have array expressions with matching dimensions
```

### Architectural Details & Indexing Strategies

- **Storage & TOAST:** Arrays are stored inline until they exceed the page size limit (typically 8KB), after which they are automatically moved to external TOAST tables. Modifying a single element in a large TOASTed array requires reading and rewriting the entire array.
- **Null Handling:** Arrays can contain `NULL` elements (e.g., `ARRAY[1, NULL, 3]`). However, checking for `NULL` elements requires caution, as `NULL = ANY(array)` evaluates to `NULL`, not `TRUE`.
- **Indexing Arrays:** Standard B-Tree indexes are not effective for array element searching (`@>`, `&&`). Instead, use **GIN (Generalized Inverted Index)**.

```sql
-- Create a GIN index for highly performant array containment and overlap queries
CREATE INDEX idx_blog_posts_tags ON blog_posts USING GIN (tags);

-- This query now uses the GIN index efficiently
SELECT title FROM blog_posts WHERE tags @> '{sql}';
```

**Best Practice:** Only use arrays for denormalized data that is inherently tied to the parent row and rarely updated independently. If you find yourself frequently updating single elements or joining array elements to other tables, use a traditional normalized one-to-many relation instead.

---

## Composite Types

A composite type represents the structure of a row or record; it is essentially a list of field names and their data types.

```sql
CREATE TYPE address AS (
    street TEXT,
    city TEXT,
    postal_code VARCHAR(20),
    country VARCHAR(2)
);

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name TEXT,
    billing_address address,
    shipping_address address,
    -- Arrays of composite types are also fully supported
    past_addresses address[]
);

-- Insert composite
INSERT INTO customers (name, billing_address)
VALUES ('Alice', ROW('123 Main St', 'NYC', '10001', 'US')); -- ROW constructor

-- Alternatively, cast from a string literal
INSERT INTO customers (name, shipping_address)
VALUES ('Bob', '("456 Elm St","LA","90001","US")'::address);
```

### Accessing & Indexing Fields

Accessing fields requires parentheses around the column name to avoid syntax ambiguity with schema/table naming.

```sql
-- Access fields
SELECT (billing_address).street FROM customers;
SELECT (billing_address).city FROM customers WHERE (billing_address).country = 'US';

-- Composite comparison
SELECT * FROM customers WHERE billing_address = shipping_address;

-- Creating an index on a specific field of a composite type
CREATE INDEX idx_customers_billing_city ON customers ((billing_address).city);
```

### Schema Migration & Dependency Tracking

Composite types create tight dependencies in PostgreSQL's catalog (`pg_type` and `pg_depend`). When you need to modify a composite type used across multiple tables, migrations can be tricky.

```sql
-- Adding an attribute is straightforward
ALTER TYPE address ADD ATTRIBUTE state VARCHAR(50) CASCADE;

-- Modifying or dropping attributes requires CASCADE to propagate to tables using the type
ALTER TYPE address DROP ATTRIBUTE postal_code CASCADE;
```

---

## Domain Types

Domains are user-defined data types that are based on existing underlying types, but include optional constraints (like `CHECK` or `NOT NULL`).

```sql
-- Create a domain for email validation using a regex CHECK constraint
CREATE DOMAIN email_address AS TEXT
    CHECK (value ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$');

-- Create a domain for strictly positive integers
CREATE DOMAIN positive_int AS INTEGER
    CHECK (value > 0);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email email_address NOT NULL,
    age positive_int
);
```

**Domain vs. Table Constraint:** Domains centralize business logic. Instead of adding `CHECK (email ~* '...')` to every table that stores an email, the domain ensures consistency across your entire schema.

---

## Range Types & Multiranges

Range types represent a contiguous range of values (e.g., timestamps, integers). PostgreSQL 14+ also introduced **multiranges**, representing non-contiguous sets of ranges.

```sql
-- Built-in ranges: INT4RANGE, INT8RANGE, NUMRANGE, TSRANGE, TSTZRANGE, DATERANGE
CREATE TABLE room_bookings (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL,
    during TSTZRANGE NOT NULL,
    
    -- Prevent double booking using an EXCLUDE constraint
    -- "No two rows can have the same room_id AND overlapping 'during' ranges"
    EXCLUDE USING gist (room_id WITH =, during WITH &&)
);

-- Range constructors. '[' means inclusive, ')' means exclusive.
SELECT '[2026-07-15 09:00, 2026-07-15 11:00)'::TSTZRANGE;
SELECT TSTZRANGE('2026-07-15 09:00', '2026-07-15 11:00', '[)');
```

### Range Operators & Indexing

```sql
-- Range operators
SELECT '[1,10)'::INT4RANGE @> 5;           -- Contains element (TRUE)
SELECT '[1,5)'::INT4RANGE @> '[2,3)'::INT4RANGE;  -- Contains range (TRUE)
SELECT '[1,5)'::INT4RANGE && '[4,8)'::INT4RANGE;  -- Overlaps (TRUE)
SELECT '[1,5)'::INT4RANGE << '[6,10)'::INT4RANGE; -- Strictly left of (TRUE)
SELECT '[1,5)'::INT4RANGE >> '[-5,0)'::INT4RANGE; -- Strictly right of (TRUE)
SELECT '[1,5)'::INT4RANGE -|- '[5,10)'::INT4RANGE; -- Adjacent (TRUE)
SELECT '[1,5)'::INT4RANGE + '[5,10)'::INT4RANGE;  -- Union: [1,10)
SELECT '[1,10)'::INT4RANGE * '[5,15)'::INT4RANGE; -- Intersection: [5,10)
SELECT '[1,10)'::INT4RANGE - '[5,7)'::INT4RANGE;  -- Difference: [1,5) and [7,10) (Returns multirange in PG14+)

-- Indexing: Range operators typically require GiST or SP-GiST indexes.
CREATE INDEX idx_room_bookings_during ON room_bookings USING GIST (during);
```

---

## Network Types

Network types optimize storage and provide robust operators for IP and MAC addresses.

- `INET`: Holds an IP address, and optionally the subnet mask.
- `CIDR`: Holds a network specification. Unlike `INET`, a `CIDR` value must have zeroed bits to the right of the netmask.
- `MACADDR` / `MACADDR8`: Holds MAC addresses.

```sql
CREATE TABLE network_devices (
    id SERIAL PRIMARY KEY,
    ip_address INET,           -- IPv4 or IPv6 host
    network CIDR,              -- Network address
    mac MACADDR,               -- MAC address
    mac8 MACADDR8              -- EUI-64
);

INSERT INTO network_devices (ip_address, network, mac)
VALUES ('192.168.1.100', '192.168.1.0/24', '08:00:2b:01:02:03');

-- Network operators
SELECT ip_address << network FROM network_devices;  -- Is strictly contained by
SELECT '192.168.1.0/24'::CIDR >> '192.168.1.5'::INET;  -- Contains
SELECT '192.168.1.0/24'::CIDR && '192.168.1.128/25'::CIDR;  -- Overlaps

-- Network functions
SELECT broadcast('192.168.1.0/24'::CIDR);  -- 192.168.1.255
SELECT host('192.168.1.0/24'::CIDR);       -- 192.168.1.0 (Returns TEXT)
SELECT masklen('192.168.1.0/24'::CIDR);    -- 24
SELECT netmask('192.168.1.0/24'::CIDR);    -- 255.255.255.0
SELECT family('::1'::INET);                -- 6 (IPv6)

-- Indexing: Use GiST indexes for subnet containment operators (<<, >>, &&)
CREATE INDEX idx_network_devices_network ON network_devices USING GIST (network inet_ops);
```

---

## Geometric Types & PostGIS

PostgreSQL has legacy built-in 2D geometric types. 

```sql
CREATE TABLE spatial_data (
    id SERIAL PRIMARY KEY,
    pt POINT,         -- (x,y)
    ln LINE,          -- Infinite line
    lseg LSEG,        -- Line segment
    bx BOX,           -- Rectangular box
    pth PATH,         -- Closed or open path
    plg POLYGON,      -- Polygon
    cr CIRCLE         -- Circle
);

-- Operators
SELECT POINT '(0,0)' <-> POINT '(3,4)';    -- Distance: 5
SELECT CIRCLE '<(0,0),1>' @> POINT '(0,0)'; -- Contains
```

### The Standard for Spatial Data: PostGIS

For any serious Geographic Information System (GIS) application, **abandon the built-in geometric types and use the PostGIS extension**. PostGIS provides advanced spatial projections, 3D/4D geometry, raster data support, and conforms to Open Geospatial Consortium (OGC) standards.

```sql
CREATE EXTENSION postgis;

CREATE TABLE restaurants (
    id SERIAL PRIMARY KEY,
    name TEXT,
    -- GEOGRAPHY type handles calculations over the curvature of the Earth (spheroid)
    -- 4326 is the SRID (Spatial Reference System Identifier) for WGS 84 (standard GPS coords)
    location GEOGRAPHY(POINT, 4326)
);

INSERT INTO restaurants (name, location)
VALUES ('Central Park Cafe', ST_GeogFromText('SRID=4326;POINT(-73.9654 40.7829)'));

-- Find restaurants within 5 kilometers (5000 meters) of a user's location
SELECT name FROM restaurants
WHERE ST_DWithin(
    location,
    ST_GeogFromText('SRID=4326;POINT(-73.9851 40.7589)'),
    5000
);

-- Spatial Indexing (Crucial for PostGIS performance)
CREATE INDEX idx_restaurants_location ON restaurants USING GIST (location);
```

---

## Vector Search for AI (pgvector)

The `pgvector` extension has become the industry standard for storing and querying AI-generated embeddings (high-dimensional vectors) directly within PostgreSQL, facilitating Retrieval-Augmented Generation (RAG) and semantic search architectures.

```sql
CREATE EXTENSION vector;

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    -- Store 1536-dimensional vectors (e.g., standard OpenAI text-embedding-3-small)
    embedding VECTOR(1536)
);

-- Insert a vector (usually provided by an AI API in reality)
INSERT INTO documents (content, embedding)
VALUES ('Machine learning in PostgreSQL', '[0.1, 0.2, 0.3, ...]');

-- Calculate distances to a target query vector
SELECT content, 
       embedding <-> '[0.1, 0.2, 0.3, ...]' AS euclidean_distance,
       embedding <=> '[0.1, 0.2, 0.3, ...]' AS cosine_distance,
       embedding <#> '[0.1, 0.2, 0.3, ...]' AS inner_product
FROM documents
ORDER BY cosine_distance ASC
LIMIT 5;
```

### Vector Indexing Strategies

Exact nearest neighbor search (KNN) requires scanning the entire table. For large datasets, Approximate Nearest Neighbor (ANN) indexes are required. `pgvector` supports two primary indexes:
1. **IVFFlat (Inverted File with Flat Compression):** Faster build times, requires the table to be populated first to calculate centroids.
2. **HNSW (Hierarchical Navigable Small World):** State-of-the-art recall and query speed. Slower to build, higher memory consumption.

```sql
-- HNSW Index for Cosine Distance (vector_cosine_ops)
-- m: max number of connections per layer, ef_construction: size of dynamic candidate list
CREATE INDEX idx_documents_embedding ON documents USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

---

## UUID

Universally Unique Identifiers are 128-bit values perfect for distributed systems, preventing ID collision and obscuring iteration logic.

```sql
-- Built-in UUID function (pgcrypto extension was historically required, but built-in as of PG 13+)
CREATE TABLE api_keys (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    key_hash TEXT NOT NULL
);

-- Generate UUID v4 (fully random)
SELECT gen_random_uuid();
```

### UUID v4 vs UUID v7

A major downside of UUID v4 is its total randomness. When used as a Primary Key, random UUIDs inserted into a B-Tree index cause immense **index bloat and page fragmentation** because rows are inserted at random locations across disk pages.

**PostgreSQL 18** natively introduces **UUIDv7**, which embeds a Unix timestamp in the leading bits. This makes UUIDv7 **time-ordered**, meaning new rows are appended to the end of the B-Tree index, solving the fragmentation problem entirely while maintaining collision resistance.

```sql
-- In PostgreSQL 18+:
-- id UUID DEFAULT uuidv7() PRIMARY KEY
```

---
*Previous: 11 - JSONB | Next: 13 - Full-Text Search*
