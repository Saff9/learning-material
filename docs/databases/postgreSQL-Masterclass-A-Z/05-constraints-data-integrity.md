# 05 - Constraints, Data Integrity & Advanced Architecture

> A masterclass on ensuring robust data integrity via constraints, custom types, domains, advanced patterns, and enterprise-grade architectural deployments including partitioning, replication, and vector search.

---

## 1. Constraint Types & Data Integrity

Constraints are the bedrock of relational databases, ensuring invalid data never enters your system. PostgreSQL offers comprehensive constraint features that perform natively at the database level.

### NOT NULL
```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,        -- Must have value
    phone VARCHAR(20)                   -- Can be NULL
);

-- Best Practice: Validate before adding to huge tables
ALTER TABLE users ADD CONSTRAINT check_email_not_null CHECK (email IS NOT NULL) NOT VALID;
ALTER TABLE users VALIDATE CONSTRAINT check_email_not_null;
-- Later, convert to actual NOT NULL which requires a full table scan lock otherwise
ALTER TABLE users ALTER COLUMN email SET NOT NULL;
ALTER TABLE users DROP CONSTRAINT check_email_not_null;
```
*Enterprise Note:* In large datasets, changing column nullability can lock the table. Using the `NOT VALID` trick helps minimize downtime in high-availability environments.

### UNIQUE
```sql
-- Single column
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL
);

-- Multi-column & Partial (Highly Recommended for Soft Deletes)
CREATE TABLE enrollments (
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    semester VARCHAR(20) NOT NULL,
    UNIQUE (student_id, course_id, semester)
);

-- Partial unique index (More flexible and space efficient)
CREATE UNIQUE INDEX idx_active_email ON users(email) WHERE is_active = TRUE;
```

### PRIMARY KEY
```sql
-- Composite PK with clustered considerations
CREATE TABLE order_items (
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (order_id, product_id)
);
```

### FOREIGN KEY
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    CONSTRAINT fk_orders_customer 
        FOREIGN KEY (customer_id) REFERENCES customers(id)
        ON DELETE RESTRICT -- Prevents deleting customer if orders exist
        ON UPDATE CASCADE
);
```
*Performance Tip:* Always index foreign keys in PostgreSQL. Unlike some databases, PG does not automatically create indexes on foreign keys, which can lead to catastrophic sequential scans during `DELETE` operations on the parent table.

### CHECK & DEFERRED CONSTRAINTS
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    price NUMERIC(10, 2) CHECK (price > 0),
    discount_price NUMERIC(10, 2),
    CONSTRAINT chk_valid_discount CHECK (discount_price IS NULL OR discount_price < price)
);
```
Sometimes you have circular references or bulk insert requirements where constraints shouldn't be checked until transaction commit.
```sql
CREATE TABLE a (id INT PRIMARY KEY, b_id INT);
CREATE TABLE b (id INT PRIMARY KEY, a_id INT);

ALTER TABLE a ADD CONSTRAINT fk_a_b FOREIGN KEY (b_id) REFERENCES b(id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE b ADD CONSTRAINT fk_b_a FOREIGN KEY (a_id) REFERENCES a(id) DEFERRABLE INITIALLY DEFERRED;
```

### EXCLUSION
```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE room_reservations (
    room_id INTEGER NOT NULL,
    during TSTZRANGE NOT NULL,
    EXCLUDE USING gist (room_id WITH =, during WITH &&)
);
```

---

## 2. Custom Types & Advanced Extensions

### Domains & Composite Types
Domains wrap existing types with a built-in `CHECK` constraint, providing type safety across the database.
```sql
CREATE DOMAIN email AS VARCHAR(255)
    CHECK (VALUE ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

CREATE DOMAIN positive_int AS INTEGER CHECK (VALUE > 0);

CREATE TYPE address AS (
    street TEXT,
    city TEXT,
    postal_code VARCHAR(20),
    country VARCHAR(2)
);
```

### Vector Search (`pgvector`)
For AI and ML applications, `pgvector` has become the standard for performing semantic searches and RAG (Retrieval-Augmented Generation) directly in PostgreSQL.
```sql
CREATE EXTENSION vector;

CREATE TABLE document_embeddings (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(1536) -- Size for OpenAI ada-002 embeddings
);

-- Nearest neighbor search (Cosine distance)
SELECT content, 1 - (embedding <=> '[0.1, 0.2, ...]') AS similarity
FROM document_embeddings
ORDER BY embedding <=> '[0.1, 0.2, ...]'
LIMIT 5;

-- Indexing for fast vector search (HNSW is recommended)
CREATE INDEX idx_doc_embedding ON document_embeddings USING hnsw (embedding vector_cosine_ops);
```

---

## 3. High Performance & Scalability

### Partitioning
When tables hit tens of millions of rows, partitioning becomes necessary to maintain index health and query performance. Declarative partitioning splits a logical large table into smaller physical pieces.
```sql
CREATE TABLE sensory_data (
    id BIGSERIAL,
    sensor_id INT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    reading NUMERIC
) PARTITION BY RANGE (recorded_at);

-- Create partitions natively
CREATE TABLE sensory_data_2026_01 PARTITION OF sensory_data
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

### Connection Pooling (`PgBouncer`)
PostgreSQL handles connections via separate OS processes, which consumes significant RAM (~10MB per connection). 
In heavy cloud deployments, you must use a connection pooler like **PgBouncer** or **Pgpool-II**.
* PgBouncer sits between your app and PG, multiplexing thousands of client connections onto a small number of actual DB connections using transaction-level pooling.

---

## 4. Security Hardening & RBAC

### Role-Based Access Control (RBAC)
Never use the superuser for application access. Implement Principle of Least Privilege.
```sql
-- Create read-only role
CREATE ROLE app_reader LOGIN PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE myapp TO app_reader;
GRANT USAGE ON SCHEMA public TO app_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO app_reader;
```

### Row-Level Security (RLS)
RLS restricts which rows a user can read/write based on their session context. Multi-tenant SaaS apps heavily rely on this.
```sql
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON tenants
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

---

## 5. Replication, DR, and Cloud Deployments

### Streaming Replication & HA
For zero-downtime, setup Primary-Replica architectures:
- **Synchronous Replication:** Transaction isn't committed until the replica confirms receipt. No data loss, but higher latency.
- **Logical Replication:** Replicates data at the table level using pub/sub models. Great for partial syncing or upgrading between major PG versions with zero downtime.

```sql
-- Logical Replication setup
CREATE PUBLICATION app_pub FOR ALL TABLES;
-- On Replica:
CREATE SUBSCRIPTION app_sub CONNECTION 'host=primary dbname=myapp...' PUBLICATION app_pub;
```

### Disaster Recovery & WAL (Point-In-Time Recovery)
PostgreSQL's Write-Ahead Log (WAL) allows for continuous archiving. Tools like **pgBackRest** or **WAL-G** can stream WAL files to S3. In a disaster, you can restore to the exact millisecond before a dropped table (Point-In-Time Recovery - PITR).

---
*Previous: 04 - Joins | Next: 06 - Indexes & Performance*
