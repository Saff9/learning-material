# 02 - Installation, Configuration & First Steps

> Covers PostgreSQL 14-18 installation on all platforms, initial security hardening, and essential tooling. It dives deep into architectural best practices, connection pooling, replication, security, disaster recovery, and advanced data types like vector search.

---

## Platform-Specific Installation & Best Practices

### Ubuntu/Debian (APT)

```bash
# Add official PostgreSQL APT repository
sudo apt install -y postgresql-common
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh

# Install PostgreSQL 18 with essential extensions (like pgvector for AI)
sudo apt update
sudo apt install -y postgresql-18 postgresql-client-18 postgresql-contrib-18 postgresql-18-pgvector

# Verify
psql --version

# Service management
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo systemctl status postgresql
```

### RHEL/CentOS/Rocky (DNF)

```bash
sudo dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm
sudo dnf -qy module disable postgresql
sudo dnf install -y postgresql18-server postgresql18-contrib pgvector_18
sudo /usr/pgsql-18/bin/postgresql-18-setup initdb
sudo systemctl enable postgresql-18
sudo systemctl start postgresql-18
```

### macOS (Homebrew)

```bash
brew install postgresql@18
brew services start postgresql@18
echo 'export PATH="/opt/homebrew/opt/postgresql@18/bin:$PATH"' >> ~/.zshrc
```

### Docker (Advanced Deployment)

A robust Docker setup should include `pgvector` for vector search, persistent storage, and optimized memory limits.

```bash
# Using a specialized image that includes pgvector and other extensions
docker run --name postgres18 \
  --memory="4g" \
  --cpus="2" \
  -e POSTGRES_PASSWORD=SecurePass123! \
  -e POSTGRES_DB=appdb \
  -e POSTGRES_USER=appuser \
  -e POSTGRES_INITDB_ARGS="--data-checksums" \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  -d ankane/pgvector:v0.5.1  # Or standard postgres:18 if you install it manually
```
*Note: `--data-checksums` is highly recommended in production to detect hardware-level corruption.*

### Cloud Deployments: AWS RDS / GCP Cloud SQL / Azure / Neon / Supabase

All major cloud providers offer managed PostgreSQL 17-18 as of 2026. However, architecture matters:
- **AWS Aurora / GCP AlloyDB**: Decouples storage from compute. Excellent for high availability and rapid scaling of read replicas.
- **Neon and Supabase**: Provide serverless PostgreSQL. They allow branching (creating a copy of the database instantly using copy-on-write) and auto-scaling (scaling compute down to zero). Watch out for "cold start" latency in serverless environments.
- **High Availability (HA)**: In the cloud, configure multi-AZ deployments for synchronous standby failover.

---

## Deep Security Hardening & RBAC

Security is a multi-layered approach. RBAC (Role-Based Access Control) should follow the principle of least privilege.

### 1. Secure the postgres Superuser

```sql
-- Lock down the default superuser
ALTER USER postgres WITH PASSWORD 'VeryStrongRandomPassword123!';
-- Create a designated human superuser (easier to audit)
CREATE ROLE dbadmin WITH LOGIN SUPERUSER CREATEDB CREATEROLE PASSWORD 'AdminPass!';
-- Prevent direct login as postgres to force using the named admin account
ALTER USER postgres WITH NOLOGIN;
```

### 2. Comprehensive Role-Based Access Control (RBAC)

Creating layered access helps when teams scale.

```sql
-- Define group roles (no login)
CREATE ROLE group_readonly;
CREATE ROLE group_readwrite;
CREATE ROLE group_ddl;

-- Grant broad schema usage
GRANT USAGE ON SCHEMA public TO group_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO group_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO group_readonly;

-- Write access
GRANT USAGE, CREATE ON SCHEMA public TO group_readwrite;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO group_readwrite;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO group_readwrite;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO group_readwrite;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON SEQUENCES TO group_readwrite;

-- Create user accounts and assign to groups
CREATE ROLE app_user WITH LOGIN PASSWORD 'SecureAppPass123!';
GRANT group_readwrite TO app_user;

CREATE ROLE analyst_user WITH LOGIN PASSWORD 'AnalystPass123!';
GRANT group_readonly TO analyst_user;
```

### 3. Row-Level Security (RLS)

To secure multi-tenant applications at the database level:

```sql
-- Enable RLS on a specific table
ALTER TABLE core.users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own row
CREATE POLICY user_isolation_policy ON core.users
    USING (id = current_setting('app.current_user_id')::bigint);
```

### 4. Network Security (pg_hba.conf & SSL)

```conf
# pg_hba.conf (Host-Based Authentication)
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                peer
local   all             all                                     scram-sha-256
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256
hostssl appdb           group_readwrite 10.0.1.0/24             scram-sha-256
hostssl appdb           group_readonly  10.0.2.0/24             scram-sha-256
# Reject everything else explicitly
host    all             all             0.0.0.0/0               reject
```

```conf
# postgresql.conf SSL Settings
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
ssl_ca_file = '/etc/ssl/certs/ca.crt'
ssl_min_protocol_version = 'TLSv1.2'
# Force clients to use strong ciphers
ssl_ciphers = 'HIGH:!aNULL:!3DES'
```

---

## Advanced Architecture & Scaling

### Connection Pooling with PgBouncer

PostgreSQL spawns a heavyweight OS process for every connection. If your app creates thousands of connections, RAM and CPU context-switching will kill performance. 

**Solution: PgBouncer** (or Pgpool-II)
Deploy PgBouncer between your app and Postgres.
- **Session Pooling**: Connection returned to pool when client disconnects.
- **Transaction Pooling**: Connection returned to pool after every transaction. Perfect for serverless apps (like AWS Lambda) that open/close connections rapidly.

### Partitioning for Massive Tables

When tables exceed ~100GB, indexes become too large to fit in memory. Declarative Partitioning splits one large table into many smaller ones.

```sql
-- Create a parent partitioned table
CREATE TABLE events (
    event_id BIGSERIAL,
    event_name VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL
) PARTITION BY RANGE (created_at);

-- Create partitions for specific months
CREATE TABLE events_2026_01 PARTITION OF events
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE events_2026_02 PARTITION OF events
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
```

### Replication & High Availability

- **Physical Streaming Replication**: Exact block-level copy of the master. Used for read replicas and HA failover.
- **Logical Replication**: Replicates data row-by-row. Useful for CDC (Change Data Capture), multi-master setups, or streaming data to a data warehouse (like Snowflake or Kafka).

### Disaster Recovery & Backups

A `pg_dump` is logical and slow to restore. For enterprise DR, use physical backups with Continuous Archiving.

- **pgBackRest or Barman**: These tools archive WAL (Write-Ahead Logs) securely to AWS S3.
- **Point-In-Time-Recovery (PITR)**: If a developer accidentally drops a table at 14:05, you can replay WAL files up to exactly 14:04 to recover the data.

---

## Essential postgresql.conf Optimization

### Memory Tuning

```conf
shared_buffers = 2GB                # ~25% of total system RAM
effective_cache_size = 6GB          # ~75% of RAM (Guides the query planner)
work_mem = 16MB                     # Memory per sort/hash operation (watch out: used per node per query!)
maintenance_work_mem = 512MB        # For VACUUM, CREATE INDEX, ALTER TABLE
wal_buffers = 16MB                  # Buffer for WAL data before writing to disk
```

### WAL & Checkpointing

Improper checkpointing is a major cause of I/O spikes.

```conf
wal_level = logical                 # Needed for logical replication and CDC
max_wal_size = 4GB                  # Target size before forced checkpoint
min_wal_size = 1GB
checkpoint_timeout = 15min          # Spread out I/O over 15 minutes
checkpoint_completion_target = 0.9  # Aim to finish checkpointing just before the next one
wal_compression = on                # Save network bandwidth and disk I/O
```

### Query Planner & Parallelism

```conf
random_page_cost = 1.1              # 1.1 for NVMe/SSD, 4.0 for HDD
effective_io_concurrency = 200      # 200+ for SSDs, 2 for HDDs
max_parallel_workers_per_gather = 4 # Max workers per individual query
max_parallel_workers = 8            # Total system parallel workers
```

### Logging & Auditing

```conf
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_min_duration_statement = 1000   # Log all queries taking > 1 second
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on                 # Crucial for debugging deadlocks
log_line_prefix = '%m [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h ' # Detailed prefix
```

### Connections & Autovacuum

```conf
max_connections = 200               # Keep low, rely on PgBouncer for scaling
autovacuum = on
autovacuum_max_workers = 4          # Increase if you have many large tables
autovacuum_vacuum_scale_factor = 0.05
autovacuum_analyze_scale_factor = 0.05
```

---

## psql Essential Commands

| Command | Description |
|---------|-------------|
| `\l` | List databases |
| `\c dbname` | Switch database |
| `\dt` | List tables |
| `\dt+` | List tables with sizes |
| `\d tablename` | Describe table structure and indexes |
| `\d+ tablename` | Describe with constraints, foreign keys, triggers |
| `\di` | List indexes |
| `\di+` | List indexes with sizes |
| `\dv` | List views |
| `\dm` | List materialized views |
| `\df` | List functions / stored procedures |
| `\dn` | List schemas |
| `\du` | List roles and permissions |
| `\dx` | List installed extensions |
| `\timing` | Toggle query execution timing |
| `\x` | Toggle expanded vertical display (perfect for wide tables) |
| `\copy table TO 'file.csv' CSV HEADER` | Export table to CSV rapidly |
| `\copy table FROM 'file.csv' CSV HEADER` | Import CSV into table rapidly |
| `\i file.sql` | Execute SQL script |
| `\q` | Quit psql |
| `\?` | psql internal command help |
| `\h CREATE TABLE` | Help on specific SQL syntax |

---

## First Database, Schema & Vector Search (pgvector)

Let's put it all together. We will create a modern database with isolated schemas and initialize the `pgvector` extension for AI-driven similarity search.

```sql
CREATE DATABASE appdb
  WITH OWNER = group_readwrite
  ENCODING = 'UTF8'
  LC_COLLATE = 'en_US.UTF-8'
  LC_CTYPE = 'en_US.UTF-8'
  TEMPLATE = template0;

\c appdb

-- Enable pgvector extension for AI / Embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Logical separation using schemas
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Adjust search path so 'core' is primary
SET search_path TO core, auth, public;

CREATE TABLE core.users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    -- Example of an embedding column for an AI matching feature (e.g. 3 dimensions for demo)
    profile_embedding vector(3) 
);

-- Insert sample users with mock embeddings
INSERT INTO core.users (email, password_hash, display_name, profile_embedding)
VALUES 
  ('alice@example.com', 'hash123', 'Alice', '[1.0, 2.0, 3.0]'),
  ('bob@example.com', 'hash456', 'Bob', '[4.0, 5.0, 6.0]');

-- Perform a Nearest Neighbor (Vector) Search
-- "Find users whose profile is most similar to [1.2, 2.1, 3.2]"
-- Uses the Euclidean distance operator (<->)
SELECT display_name, email, profile_embedding <-> '[1.2, 2.1, 3.2]' AS distance
FROM core.users
ORDER BY profile_embedding <-> '[1.2, 2.1, 3.2]'
LIMIT 5;
```

---
*Previous: 01 - Introduction | Next: 03 - SQL Fundamentals*

