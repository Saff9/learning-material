# 02 - Installation & Setup

## Installing PostgreSQL

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install PostgreSQL and contrib packages
sudo apt install postgresql postgresql-contrib

# Verify installation
psql --version

# Start the service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Check status
sudo systemctl status postgresql
```

### Linux (RHEL/CentOS/Fedora)

```bash
# Install repository
sudo dnf install https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm

# Install PostgreSQL 16
sudo dnf install postgresql16-server postgresql16-contrib

# Initialize database
sudo /usr/pgsql-16/bin/postgresql-16-setup initdb

# Start service
sudo systemctl start postgresql-16
sudo systemctl enable postgresql-16
```

### macOS

```bash
# Using Homebrew
brew install postgresql@16

# Start service
brew services start postgresql@16

# Or manually
pg_ctl -D /usr/local/var/postgresql@16 start
```

### Windows

1. Download installer from [postgresql.org/download](https://www.postgresql.org/download/)
2. Run the installer wizard
3. Set superuser (postgres) password
4. Choose port (default: 5432)
5. Select components: Server, pgAdmin, Stack Builder

### Docker

```bash
# Pull and run PostgreSQL
docker run --name my-postgres \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -e POSTGRES_DB=mydatabase \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  -d postgres:16

# Connect to container
docker exec -it my-postgres psql -U postgres -d mydatabase
```

## Initial Configuration

### Switch to postgres User

```bash
# Linux
sudo -u postgres psql

# Or switch user
sudo -i -u postgres
psql
```

### Create a New User/Role

```sql
-- Create a superuser
CREATE ROLE myuser WITH LOGIN SUPERUSER CREATEDB CREATEROLE PASSWORD 'secure_password';

-- Create a regular user
CREATE ROLE app_user WITH LOGIN PASSWORD 'app_password';

-- Create user with specific privileges
CREATE ROLE readonly WITH LOGIN PASSWORD 'readonly_pass';
GRANT CONNECT ON DATABASE mydb TO readonly;
GRANT USAGE ON SCHEMA public TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
```

### Create a Database

```sql
-- Create database
CREATE DATABASE mydb OWNER myuser;

-- With specific encoding and locale
CREATE DATABASE mydb 
  WITH 
    OWNER = myuser 
    ENCODING = 'UTF8' 
    LC_COLLATE = 'en_US.UTF-8' 
    LC_CTYPE = 'en_US.UTF-8' 
    TEMPLATE = template0;
```

### Connect to a Database

```bash
# Command line
psql -U myuser -d mydb -h localhost -p 5432

# With password prompt
psql -U myuser -d mydb -W

# Connection string format
psql "postgresql://myuser:password@localhost:5432/mydb"
```

## Essential psql Commands

| Command | Description |
|---------|-------------|
| `\l` | List all databases |
| `\c database_name` | Connect to a database |
| `\dt` | List all tables in current schema |
| `\d table_name` | Describe a table (columns, constraints, indexes) |
| `\di` | List indexes |
| `\du` | List users/roles |
| `\dn` | List schemas |
| `\df` | List functions |
| `\dv` | List views |
| `\timing` | Toggle query execution time display |
| `\x` | Toggle expanded display (vertical output) |
| `\q` | Quit psql |
| `\?` | Show psql help |
| `\h CREATE TABLE` | Show SQL syntax help |

## PostgreSQL Configuration Files

### postgresql.conf

Main configuration file. Located at:
- Linux: `/etc/postgresql/16/main/postgresql.conf`
- macOS: `/usr/local/var/postgresql@16/postgresql.conf`
- Docker: `/var/lib/postgresql/data/postgresql.conf`

```conf
# Connection Settings
listen_addresses = '*'          # Listen on all interfaces (default: localhost)
port = 5432
max_connections = 100

# Memory Settings
shared_buffers = 256MB          # ~25% of RAM (default: 128MB)
effective_cache_size = 768MB    # ~75% of RAM
work_mem = 4MB                  # Per-operation sort/hash memory
maintenance_work_mem = 64MB     # For VACUUM, CREATE INDEX, etc.

# WAL (Write-Ahead Log) Settings
wal_level = replica
max_wal_size = 1GB
min_wal_size = 80MB

# Query Planner
random_page_cost = 1.1          # Lower for SSD, higher for HDD
effective_io_concurrency = 200  # For SSDs

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_min_duration_statement = 1000  # Log queries > 1000ms
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

### pg_hba.conf

Client authentication configuration:

```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local connections (Unix socket)
local   all             all                                     scram-sha-256

# IPv4 local connections
host    all             all             127.0.0.1/32            scram-sha-256

# IPv6 local connections
host    all             all             ::1/128                 scram-sha-256

# Allow specific network
host    mydb            app_user        10.0.0.0/24             scram-sha-256

# Allow all from specific IP (not recommended for production)
host    all             all             192.168.1.100/32        trust
```

Authentication methods:
- **trust**: No password required (development only!)
- **scram-sha-256**: Secure password hashing (recommended)
- **md5**: Legacy password hashing
- **peer**: OS user must match DB user (local only)
- **ident**: Uses OS ident service
- **ldap**: LDAP authentication
- **cert**: SSL certificate authentication

### pg_ident.conf

Maps OS users to database users:

```conf
# MAPNAME       SYSTEM-USERNAME         PG-USERNAME
mymap           john_doe                db_admin
mymap           /^(.*)@domain\.com$    \1
```

## Environment Variables

```bash
# Set default connection parameters
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=mydb
export PGUSER=myuser
export PGPASSWORD=mypassword  # Use .pgpass instead for security

# Alternative: .pgpass file (chmod 600)
# Format: hostname:port:database:username:password
echo "localhost:5432:mydb:myuser:mypassword" > ~/.pgpass
chmod 600 ~/.pgpass
```

## Creating Your First Table

```sql
-- Connect to database
\c mydb

-- Create a simple table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Insert data
INSERT INTO users (username, email) 
VALUES ('alice', 'alice@example.com'),
       ('bob', 'bob@example.com');

-- Query data
SELECT * FROM users;

-- Clean up
DROP TABLE users;
```

## Summary

You now have PostgreSQL installed, configured, and running. You understand:
- How to install on different platforms
- Basic user and database management
- Essential psql commands
- Key configuration files and their purposes
- How to create your first table

---
*Previous: [01 - Introduction](01-introduction.md) | Next: [03 - SQL Fundamentals](03-sql-fundamentals.md)*
