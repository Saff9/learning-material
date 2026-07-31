# 02 - Installation, Configuration & First Steps

> Covers PostgreSQL 14-18 installation on all platforms, initial security hardening, and essential tooling.

---

## Platform-Specific Installation

### Ubuntu/Debian (APT)

```bash
# Add official PostgreSQL APT repository
sudo apt install -y postgresql-common
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh

# Install PostgreSQL 18
sudo apt update
sudo apt install -y postgresql-18 postgresql-client-18 postgresql-contrib-18

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
sudo dnf install -y postgresql18-server postgresql18-contrib
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

### Docker

```bash
docker run --name postgres18 \
  -e POSTGRES_PASSWORD=SecurePass123! \
  -e POSTGRES_DB=appdb \
  -e POSTGRES_USER=appuser \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  -d postgres:18
```

### Cloud: AWS RDS / GCP Cloud SQL / Azure / Neon / Supabase

All major cloud providers offer managed PostgreSQL 17-18 as of 2026.
Neon and Supabase provide serverless PostgreSQL with branching and auto-scaling.

---

## Initial Security Hardening

### 1. Secure the postgres Superuser

```sql
ALTER USER postgres WITH PASSWORD 'VeryStrongRandomPassword123!';
CREATE ROLE dbadmin WITH LOGIN SUPERUSER CREATEDB CREATEROLE PASSWORD 'AdminPass!';
ALTER USER postgres WITH NOLOGIN;
```

### 2. Create Application Roles

```sql
-- Read-only role
CREATE ROLE app_readonly WITH LOGIN PASSWORD 'ReadOnlyPass!';
GRANT CONNECT ON DATABASE appdb TO app_readonly;
GRANT USAGE ON SCHEMA public TO app_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO app_readonly;

-- Read-write role
CREATE ROLE app_readwrite WITH LOGIN PASSWORD 'ReadWritePass!';
GRANT CONNECT ON DATABASE appdb TO app_readwrite;
GRANT USAGE, CREATE ON SCHEMA public TO app_readwrite;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_readwrite;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_readwrite;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_readwrite;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON SEQUENCES TO app_readwrite;
```

### 3. Configure pg_hba.conf

```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                peer
local   all             all                                     scram-sha-256
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256
hostssl appdb           app_readwrite   10.0.1.0/24             scram-sha-256
hostssl appdb           app_readonly    10.0.2.0/24             scram-sha-256
host    all             all             0.0.0.0/0               reject
```

### 4. Enable SSL/TLS

```conf
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
ssl_ca_file = '/etc/ssl/certs/ca.crt'
ssl_min_protocol_version = 'TLSv1.2'
```

---

## Essential postgresql.conf

### Memory Tuning

```conf
shared_buffers = 2GB                # 25% of RAM
effective_cache_size = 6GB          # 75% of RAM
work_mem = 16MB                     # Per operation
maintenance_work_mem = 512MB        # VACUUM, CREATE INDEX
wal_buffers = 16MB
```

### WAL & Checkpointing

```conf
wal_level = replica
max_wal_size = 4GB
min_wal_size = 1GB
checkpoint_completion_target = 0.9
wal_compression = on
```

### Query Planner

```conf
random_page_cost = 1.1              # 1.1 SSD, 4.0 HDD
effective_io_concurrency = 200      # 200 SSD, 2 HDD
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
```

### Logging

```conf
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

### Connection & Vacuum

```conf
max_connections = 200
autovacuum = on
autovacuum_max_workers = 3
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
| `\d tablename` | Describe table |
| `\d+ tablename` | Describe with details |
| `\di` | List indexes |
| `\di+` | List indexes with sizes |
| `\dv` | List views |
| `\dm` | List materialized views |
| `\df` | List functions |
| `\dn` | List schemas |
| `\du` | List roles |
| `\dx` | List extensions |
| `\timing` | Toggle query timing |
| `\x` | Toggle expanded display |
| `\copy table TO 'file.csv' CSV HEADER` | Export CSV |
| `\copy table FROM 'file.csv' CSV HEADER` | Import CSV |
| `\i file.sql` | Execute SQL file |
| `\q` | Quit |
| `\?` | psql help |
| `\h CREATE TABLE` | SQL syntax help |

---

## First Database & Schema

```sql
CREATE DATABASE appdb
  WITH OWNER = app_readwrite
  ENCODING = 'UTF8'
  LC_COLLATE = 'en_US.UTF-8'
  LC_CTYPE = 'en_US.UTF-8'
  TEMPLATE = template0;

\c appdb

CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS analytics;

SET search_path TO core, auth, public;

CREATE TABLE core.users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

INSERT INTO core.users (email, password_hash, display_name)
VALUES ('alice@example.com', 'hash123', 'Alice'),
       ('bob@example.com', 'hash456', 'Bob');

SELECT * FROM core.users;
```

---
*Previous: 01 - Introduction | Next: 03 - SQL Fundamentals*
