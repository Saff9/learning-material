# 06 - Indexes, Performance & Advanced Architecture Foundations

> A comprehensive deep dive into every index type, vector search (pgvector), query tuning, scaling via partitioning, connection pooling (PgBouncer), replication, and security hardening.

---

## 1. Index Types & Deep Mechanics

### B-tree (Balanced Tree, Default)
Best for: equality (`=`), range (`<`, `>`, `BETWEEN`), `LIKE 'prefix%'`, `ORDER BY`.

*Architectural Detail*: PostgreSQL B-Trees use the Lehman and Yao concurrency algorithm to allow multiple processes to read and write without locking the entire index. They maintain a balanced height, making lookup time predictable `O(log N)`.

```sql
CREATE INDEX idx_employees_name ON employees(last_name);
CREATE INDEX idx_employees_name_first ON employees(last_name, first_name);
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- Expression index (avoids runtime computation overhead)
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- Partial index (dramatically smaller, faster for common query patterns)
CREATE INDEX idx_active_users ON users(last_name) WHERE is_active = TRUE;

-- Include columns (covering index, PG 11+)
CREATE INDEX idx_employees_dept ON employees(department_id) INCLUDE (salary, last_name);
```
**Edge Case:** `FILLFACTOR` tuning. For write-heavy tables, setting index `FILLFACTOR` lower than 100 (e.g., 90) leaves room for updates, reducing page splits and WAL bloat.

### Hash
Best for: exact equality only (no ranges).

*Architectural Detail*: Historically discouraged, but since PG 10+, Hash indexes are WAL-logged, making them crash-safe and replicable. They can be smaller and faster than B-Trees for pure equality checks on large inputs (e.g., UUIDs).

```sql
CREATE INDEX idx_users_email_hash ON users USING hash(email);
-- Only supports: WHERE email = 'exact@match.com'
-- Cannot use: WHERE email > 'a'
```

### GiST (Generalized Search Tree)
Best for: geometric, range types, full-text, nearest-neighbor. GiST allows building arbitrary index structures (like R-trees).

```sql
-- Range data (prevents overlapping bookings using EXCLUDE)
CREATE INDEX idx_reservations ON room_reservations USING gist(during);
ALTER TABLE room_reservations ADD CONSTRAINT no_overlap EXCLUDE USING gist (room_id WITH =, during WITH &&);

-- Full-text search
CREATE INDEX idx_posts_fts ON posts USING gist(to_tsvector('english', content));

-- Geometric (with PostGIS)
CREATE INDEX idx_locations ON places USING gist(geom);
```

### GIN (Generalized Inverted Index)
Best for: arrays, JSONB, full-text (read-heavy). Works by mapping each element (e.g., array item, lexeme) to the rows containing it.

*Architectural Detail*: GIN inserts can be slow. Use `fastupdate = on` (default) to buffer inserts in a pending list, which gets flushed during VACUUM.

```sql
-- Array contains
CREATE INDEX idx_posts_tags ON posts USING gin(tags);
-- WHERE tags @> ARRAY['postgresql']

-- JSONB
CREATE INDEX idx_products_data ON products USING gin(data);
-- WHERE data @> '{"category": "electronics"}'

-- GIN with path ops (smaller, faster for @> operator on JSONB)
CREATE INDEX idx_products_data_path ON products USING gin(data jsonb_path_ops);
```

### BRIN (Block Range Index)
Best for: very large, naturally ordered tables (logs, IoT data). It stores the min/max values for a block of pages.

```sql
-- Time-series data
CREATE INDEX idx_events_created ON events USING brin(created_at);
-- A 10TB table might have a BRIN index of just a few Megabytes!
-- Edge case: If data isn't inserted in strict order, BRIN loses its effectiveness.
```

### SP-GiST (Space-Partitioned GiST)
Best for: highly clustered data with unbalanced tree structures (e.g., IP addresses, phone numbers, suffix trees).

```sql
CREATE INDEX idx_networks ON networks USING spgist(ip_address);
```

---

## 2. Advanced Search: Vector Databases with `pgvector`

With AI/ML applications, exact match isn't enough. `pgvector` adds Vector similarity search to Postgres.

```sql
CREATE EXTENSION vector;

-- Store embeddings (e.g., OpenAI 1536-dimensional vectors)
CREATE TABLE documents (
    id bigserial PRIMARY KEY,
    content text,
    embedding vector(1536)
);

-- HNSW (Hierarchical Navigable Small World) Index - PG 16+
-- Best for fast, highly accurate approximate nearest neighbor (ANN) search.
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);

-- IVFFlat (Inverted File with Flat Compression)
-- Requires data to be loaded before creation to calculate centroids (K-Means).
CREATE INDEX ON documents USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

-- Query: Find top 5 similar documents (Cosine distance)
SELECT id, content FROM documents 
ORDER BY embedding <=> '[0.1, 0.2, ...]' 
LIMIT 5;
```

---

## 3. Advanced Index Features & Tuning

### Covering Indexes (INCLUDE) and Visibility Map
```sql
CREATE INDEX idx_employees_covering ON employees(department_id) 
INCLUDE (salary, last_name, first_name);
```
**Index-Only Scans**: When a query requests only columns in the index, PG tries to skip reading the table. However, it must check the **Visibility Map** to ensure the row is visible to the current transaction. If the table is heavily updated and rarely vacuumed, the Visibility Map gets outdated, forcing a fallback to a regular Index Scan.

### Multi-Column Index Column Order
The order matters immensely. Follow the **Equality-Range-Sort** rule:
1. Columns used with `=`
2. Columns used for ranges (`<`, `>`)
3. Columns used in `ORDER BY`

### Concurrent Creation & Maintenance
```sql
-- No table locks, safe for production, but takes longer and may fail on deadlocks
CREATE INDEX CONCURRENTLY idx_employees_name ON employees(name);
```

Check index sizes and hit rates using `pg_stat_user_indexes`:
```sql
SELECT indexrelname, pg_size_pretty(pg_relation_size(indexrelid)) as size,
       idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE relname = 'employees';
```
**Reindexing**: Bloat happens due to MVCC (updates create dead tuples). Use `REINDEX INDEX CONCURRENTLY my_idx;` to clear bloat without locking.

---

## 4. Scaling: Partitioning & Connection Pooling

### Table Partitioning
When tables exceed 100GB, indexes no longer fit in RAM, and maintenance (Vacuum/Reindex) becomes a nightmare. Use **Declarative Partitioning**.

```sql
-- Partition by Time
CREATE TABLE events (
    id bigserial,
    event_type text,
    created_at timestamp NOT NULL
) PARTITION BY RANGE (created_at);

-- Create Partitions
CREATE TABLE events_2024_01 PARTITION OF events FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```
*Best Practice*: **Partition Pruning**. With partitioning, `SELECT * FROM events WHERE created_at = '2024-01-15'` will entirely ignore the other months' partitions, bypassing massive amounts of disk I/O.

### Connection Pooling (PgBouncer)
Postgres uses a process-per-connection model. 1000 idle connections = 1000 OS processes, eating all RAM.
- **PgBouncer** sits in front of PG, multiplexing thousands of app connections down to ~50 real PG connections.
- Use **Transaction Mode** pooling for typical REST/GraphQL backends.

---

## 5. Security Hardening & RBAC

### Row-Level Security (RLS)
Ensure multi-tenant apps never leak data across tenants at the database level.

```sql
ALTER TABLE tenant_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON tenant_data
    USING (tenant_id = current_setting('app.current_tenant')::int);
```

### Role-Based Access Control (RBAC)
Never use the `postgres` superuser for applications.
```sql
CREATE ROLE read_only;
GRANT CONNECT ON DATABASE app_db TO read_only;
GRANT USAGE ON SCHEMA public TO read_only;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO read_only;
-- Ensure future tables are covered
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO read_only;
```

---

## 6. High Availability (HA) & Disaster Recovery

- **WAL (Write-Ahead Logging)**: Every change is written to WAL before data files. This guarantees durability (ACID).
- **Streaming Replication**: Primary streams WAL to Read-Replicas asynchronously (or synchronously for zero-data-loss). Offload reporting and heavy `SELECT` queries to replicas.
- **Logical Replication**: Replicate specific tables (pub/sub). Great for migrating across PG versions with zero downtime or sending data to a data warehouse.
- **Point-In-Time Recovery (PITR)**: By backing up WAL files to S3 (e.g., using `pgBackRest` or `WAL-G`), you can restore the DB to exactly 2:14:32 PM before an accidental `DROP TABLE` occurred.

---

## 7. Golden Best Practices Summary

1. **Always index foreign keys** — critical for JOIN performance and cascading deletes.
2. **Follow the Equality-Range-Sort rule** when ordering columns in composite indexes.
3. **Use partial indexes** for filtered queries — huge space saver.
4. **Don't over-index** — every index adds latency to `INSERT`/`UPDATE`/`DELETE`.
5. **Monitor with pg_stat_statements** — track which queries are actually consuming the most total time (`total_exec_time`).
6. **Use CONCURRENTLY in production** — avoid table locks.
7. **Tune Autovacuum** — aggressive autovacuum prevents index bloat and transaction ID wraparound. Don't turn it off!
8. **Never exceed max_connections (e.g. >300)** — use PgBouncer for high concurrency.

---
*Previous: 05 - Constraints | Next: 07 - Advanced SQL*
