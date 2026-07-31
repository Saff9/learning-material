# 12 - Arrays, Composite Types & Specialized Data

> Arrays, composite types, ranges, network types, geometric types, and UUID.

---

## Arrays

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

-- Array literals
INSERT INTO blog_posts (title, tags)
VALUES ('Advanced SQL', '{advanced,sql,optimization}');

-- Access elements
SELECT tags[1] FROM blog_posts;           -- First element (1-indexed!)
SELECT tags[1:2] FROM blog_posts;         -- Slice

-- Array operations
SELECT * FROM blog_posts WHERE tags @> ARRAY['sql'];        -- Contains
SELECT * FROM blog_posts WHERE tags <@ ARRAY['sql','db'];   -- Contained in
SELECT * FROM blog_posts WHERE tags && ARRAY['sql'];        -- Overlap
SELECT * FROM blog_posts WHERE 'sql' = ANY(tags);           -- Any element
SELECT * FROM blog_posts WHERE ARRAY['sql','db'] = ALL(tags); -- All elements

-- Array functions
SELECT array_length(tags, 1) FROM blog_posts;       -- Dimension length
SELECT array_dims(tags) FROM blog_posts;            -- Dimensions
SELECT array_append(tags, 'new') FROM blog_posts;   -- Add element
SELECT array_prepend('new', tags) FROM blog_posts;  -- Prepend
SELECT array_remove(tags, 'sql') FROM blog_posts;   -- Remove value
SELECT array_position(tags, 'sql') FROM blog_posts; -- Find position
SELECT array_distinct(tags) FROM blog_posts;        -- Unique values
SELECT array_sort(tags) FROM blog_posts;            -- Sort
SELECT array_agg(name ORDER BY name) FROM employees; -- Aggregate to array
SELECT unnest(tags) FROM blog_posts;                -- Expand to rows

-- Multidimensional
SELECT matrix[1][2] FROM blog_posts;
```

---

## Composite Types

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
    shipping_address address
);

-- Insert composite
INSERT INTO customers (name, billing_address)
VALUES ('Alice', ('123 Main St', 'NYC', '10001', 'US'));

-- Access fields
SELECT (billing_address).street FROM customers;
SELECT (billing_address).city FROM customers WHERE (billing_address).country = 'US';

-- Composite comparison
SELECT * FROM customers WHERE billing_address = shipping_address;

-- Row constructor
SELECT ROW('Alice', 30, 'Engineer');
```

---

## Range Types

```sql
CREATE TABLE room_bookings (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL,
    during TSTZRANGE NOT NULL,
    EXCLUDE USING gist (room_id WITH =, during WITH &&)
);

-- Range constructors
SELECT '[2026-07-15 09:00, 2026-07-15 11:00)'::TSTZRANGE;
SELECT TSTZRANGE('2026-07-15 09:00', '2026-07-15 11:00', '[)');

-- Range operators
SELECT '[1,10)'::INT4RANGE @> 5;           -- Contains element
SELECT '[1,5)'::INT4RANGE @> '[2,3)'::INT4RANGE;  -- Contains range
SELECT '[1,5)'::INT4RANGE && '[4,8)'::INT4RANGE;  -- Overlaps
SELECT '[1,5)'::INT4RANGE << '[6,10)'::INT4RANGE; -- Strictly left
SELECT '[1,5)'::INT4RANGE >> '[-5,0)'::INT4RANGE; -- Strictly right
SELECT '[1,5)'::INT4RANGE -|- '[5,10)'::INT4RANGE; -- Adjacent
SELECT '[1,5)'::INT4RANGE + '[5,10)'::INT4RANGE;  -- Union
SELECT '[1,10)'::INT4RANGE * '[5,15)'::INT4RANGE; -- Intersection
SELECT '[1,10)'::INT4RANGE - '[5,7)'::INT4RANGE;  -- Difference
SELECT lower('[1,10)'::INT4RANGE);          -- Lower bound
SELECT upper('[1,10)'::INT4RANGE);          -- Upper bound
SELECT isempty('[1,1)'::INT4RANGE);         -- TRUE
SELECT lower_inc('[1,10)'::INT4RANGE);      -- TRUE (inclusive)
SELECT upper_inc('[1,10)'::INT4RANGE);      -- FALSE (exclusive)
```

---

## Network Types

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
SELECT ip_address << network FROM network_devices;  -- Is contained within
SELECT '192.168.1.0/24'::CIDR >> '192.168.1.5'::INET;  -- Contains
SELECT '192.168.1.0/24'::CIDR && '192.168.1.128/25'::CIDR;  -- Overlaps
SELECT broadcast('192.168.1.0/24'::CIDR);  -- 192.168.1.255
SELECT host('192.168.1.0/24'::CIDR);       -- 192.168.1.0
SELECT masklen('192.168.1.0/24'::CIDR);    -- 24
SELECT netmask('192.168.1.0/24'::CIDR);    -- 255.255.255.0
SELECT network('192.168.1.100/24'::INET);  -- 192.168.1.0/24
SELECT abbrev('192.168.1.0/24'::CIDR);     -- 192.168.1.0/24
SELECT family('::1'::INET);                -- 6 (IPv6)
```

---

## Geometric Types (Built-in)

```sql
CREATE TABLE spatial_data (
    id SERIAL PRIMARY KEY,
    pt POINT,
    ln LINE,
    lseg LSEG,        -- Line segment
    bx BOX,
    pth PATH,
    plg POLYGON,
    cr CIRCLE
);

-- Operators
SELECT POINT '(0,0)' <-> POINT '(3,4)';    -- Distance: 5
SELECT CIRCLE '<(0,0),1>' @> POINT '(0,0)'; -- Contains
```

> For serious GIS work, use **PostGIS** extension instead of built-in geometric types.

---

## UUID

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE api_keys (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    key_hash TEXT NOT NULL
);

-- PostgreSQL 18: UUIDv7 (time-ordered, index-friendly)
-- id UUID DEFAULT uuidv7() PRIMARY KEY

-- Generate UUIDs
SELECT gen_random_uuid();
-- SELECT uuidv7();  -- PG 18+
```

---
*Previous: 11 - JSONB | Next: 13 - Full-Text Search*
