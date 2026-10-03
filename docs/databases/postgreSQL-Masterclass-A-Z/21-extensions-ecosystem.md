# 21 - Extensions & Ecosystem

> PostgreSQL's superpower is its extensibility. Essential extensions: PostGIS, pgvector, pg_trgm, pg_cron, FDW, and more.

---

## Managing Extensions

Extensions are loaded dynamically. Many cloud providers pre-install popular extensions, but you must enable them per-database.

```sql
-- List available extensions installed on the OS/Server
SELECT name, default_version, installed_version, comment 
FROM pg_available_extensions;

-- Enable an extension in the current database
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Upgrade an extension to a newer version
ALTER EXTENSION pg_trgm UPDATE;

-- Check currently enabled extensions
SELECT * FROM pg_extension;
```

---

## 1. Text Search and Indexing (`pg_trgm`)

`pg_trgm` provides functions and index operators for determining the alphanumeric similarity of text based on trigram matching (breaking words into 3-letter sequences). It is crucial for **Fuzzy Searching** and `LIKE`/`ILIKE` query optimization.

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Similarity score (0.0 to 1.0)
SELECT similarity('postgresql', 'postgres');  -- Returns ~0.71

-- Creating a GiST or GIN index for trigrams
-- GIN is generally faster for reads but slower to build
CREATE INDEX idx_users_name_trgm ON users USING gin (name gin_trgm_ops);

-- Optimizing LIKE/ILIKE queries
-- Without the index, this does a sequential scan. With pg_trgm, it uses the index!
SELECT * FROM users WHERE name ILIKE '%john%';

-- Fuzzy search threshold search (finds names similar to 'Alce')
SET pg_trgm.similarity_threshold = 0.4;
SELECT * FROM users WHERE name % 'Alce'; 
```

---

## 2. Geospatial and GIS (`PostGIS`)

PostGIS turns PostgreSQL into a state-of-the-art geographic information system. It handles geometry, geography, spatial indexing, and complex routing.

```sql
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create table with GEOGRAPHY (accounting for Earth's curvature)
CREATE TABLE delivery_zones (
    id SERIAL PRIMARY KEY,
    name TEXT,
    polygon_area GEOGRAPHY(POLYGON, 4326), -- SRID 4326 is standard GPS coordinates
    center_point GEOGRAPHY(POINT, 4326)
);

-- Spatial indexing (GiST is highly optimized for multi-dimensional data)
CREATE INDEX idx_zones_area ON delivery_zones USING gist(polygon_area);

-- Advanced Geospatial Queries:
-- 1. Point in Polygon (Is the user in the delivery zone?)
SELECT name FROM delivery_zones 
WHERE ST_Covers(polygon_area, ST_MakePoint(-73.935242, 40.730610)::GEOGRAPHY);

-- 2. K-Nearest Neighbors (Find 5 closest coffee shops)
SELECT name, 
       ST_Distance(center_point, ST_MakePoint(-73.9, 40.7)::GEOGRAPHY) AS dist_meters
FROM delivery_zones
ORDER BY center_point <-> ST_MakePoint(-73.9, 40.7)::GEOGRAPHY
LIMIT 5;
```

---

## 3. Distributed Data (`postgres_fdw`)

Foreign Data Wrappers (FDW) allow you to connect to and query external databases directly from within PostgreSQL. `postgres_fdw` connects to other Postgres instances.

```sql
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

-- 1. Define the remote server
CREATE SERVER reporting_db_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host 'reporting.internal', dbname 'analytics_db', port '5432');

-- 2. Map local user to remote user credentials
CREATE USER MAPPING FOR current_user
SERVER reporting_db_server
OPTIONS (user 'fdw_user', password 'super_secret');

-- 3. Import specific tables or a whole schema
IMPORT FOREIGN SCHEMA public LIMIT TO (historical_sales, logs)
FROM SERVER reporting_db_server INTO public;

-- 4. Query seamlessly (Postgres pushes down WHERE clauses to the remote server)
SELECT * FROM historical_sales WHERE year = 2023;
```

> **Note:** FDWs exist for MySQL (`mysql_fdw`), MongoDB (`mongo_fdw`), Redis, CSV files (`file_fdw`), and even APIs.

---

## 4. Job Scheduling (`pg_cron`)

Run scheduled jobs directly inside the database without relying on external cron servers.

```sql
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Schedule jobs using standard cron syntax
-- Run a complex materialized view refresh every night at 3 AM
SELECT cron.schedule('refresh-daily-reports', '0 3 * * *', 'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_sales');

-- Delete old audit logs every Sunday at 1 AM
SELECT cron.schedule('cleanup-logs', '0 1 * * 0', 'DELETE FROM audit_logs WHERE created_at < NOW() - INTERVAL ''90 days''');

-- Review job status and history
SELECT * FROM cron.job;
SELECT * FROM cron.job_run_details ORDER BY start_time DESC LIMIT 10;

-- Unschedule a job
SELECT cron.unschedule('cleanup-logs');
```

---

## 5. Other Essential Extensions in the Ecosystem

| Extension | Domain | Purpose |
|-----------|--------|---------|
| **`pgvector`** | AI / ML | Vector embeddings storage and similarity search (See Chapter 22). |
| **`TimescaleDB`** | Time Series | Automatic partitioning for time-series data, continuous aggregates, and compression. |
| **`pgAudit`** | Security | Detailed session and object audit logging (HIPAA/SOC2 compliance). |
| **`pg_partman`** | Partitioning | Extension to automate table partition creation and maintenance (by time or ID). |
| **`pg_repack`** | Maintenance | Removes table bloat (VACUUM FULL alternative) *without* locking the table. |
| **`hypopg`** | Tuning | Create "hypothetical" indexes to test if the query planner would use them, without building them. |
| **`pgcrypto`** | Security | Cryptographic functions (hashing, encryption, UUID generation). |
| **`Citus`** | Scaling | Transforms Postgres into a distributed database, sharding data across multiple nodes. |

---
*Previous: 20 - Performance | Next: 22 - AI & Vector Workloads*
