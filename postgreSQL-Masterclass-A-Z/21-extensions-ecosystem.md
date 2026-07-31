# 21 - Extensions & Ecosystem

> Essential extensions: PostGIS, pgvector, pg_trgm, pg_cron, FDW, and more.

---

## Installing Extensions

```sql
-- List available
SELECT * FROM pg_available_extensions;

-- Install
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Check installed
SELECT * FROM pg_extension;
```

---

## pg_trgm (Fuzzy Text Search)

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Similarity search
SELECT similarity('hello', 'hallo');  -- 0.5

-- Index for similarity
CREATE INDEX idx_names_trgm ON users USING gin (name gin_trgm_ops);

-- Fuzzy search
SELECT * FROM users WHERE name % 'Alce';  -- Similar to 'Alce'
SELECT * FROM users WHERE similarity(name, 'Alce') > 0.3;
```

---

## pg_cron (Job Scheduling)

```sql
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Schedule jobs
SELECT cron.schedule('nightly-vacuum', '0 2 * * *', 'VACUUM ANALYZE');
SELECT cron.schedule('refresh-mv', '0 3 * * *', 'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_stats');

-- List jobs
SELECT * FROM cron.job;

-- Unschedule
SELECT cron.unschedule('nightly-vacuum');
```

---

## PostGIS (Geospatial)

```sql
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create table with geometry
CREATE TABLE places (
    id SERIAL PRIMARY KEY,
    name TEXT,
    location GEOGRAPHY(POINT, 4326)
);

-- Insert
INSERT INTO places (name, location)
VALUES ('NYC', ST_SetSRID(ST_MakePoint(-74.006, 40.7128), 4326));

-- Find nearby
SELECT name, ST_Distance(location::GEOGRAPHY, 
    ST_SetSRID(ST_MakePoint(-74.006, 40.7128), 4326)::GEOGRAPHY) AS distance
FROM places
WHERE ST_DWithin(location::GEOGRAPHY, 
    ST_SetSRID(ST_MakePoint(-74.006, 40.7128), 4326)::GEOGRAPHY, 10000)
ORDER BY distance;

-- Spatial index
CREATE INDEX idx_places_location ON places USING gist(location);
```

---

## Foreign Data Wrappers (FDW)

```sql
-- postgres_fdw
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

CREATE SERVER remote_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host 'remote-host', dbname 'remote_db', port '5432');

CREATE USER MAPPING FOR current_user
SERVER remote_server
OPTIONS (user 'remote_user', password 'remote_pass');

IMPORT FOREIGN SCHEMA public LIMIT TO (users, orders)
FROM SERVER remote_server INTO public;

-- Query remote tables
SELECT * FROM users;  -- Actually queries remote server
```

---

## Other Useful Extensions

| Extension | Purpose |
|-----------|---------|
| `pg_stat_statements` | Query statistics |
| `auto_explain` | Automatic EXPLAIN for slow queries |
| `pg_buffercache` | Shared buffer inspection |
| `pg_prewarm` | Preload tables into buffer cache |
| `uuid-ossp` | UUID generation (legacy, use pgcrypto) |
| `pgcrypto` | Cryptographic functions |
| `hstore` | Key-value pairs (use JSONB instead) |
| `ltree` | Hierarchical tree-like data |
| `cube` | Multi-dimensional cubes |
| `intarray` | Integer array operations |
| `pg_similarity` | Advanced similarity measures |
| `pg_repack` | Online table reorganization |
| `hypopg` | Hypothetical indexes (test without creating) |

---
*Previous: 20 - Performance | Next: 22 - AI & Vector Workloads*
