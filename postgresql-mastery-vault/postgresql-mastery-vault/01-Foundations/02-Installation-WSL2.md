---
tags: [postgresql, foundations, installation, wsl2]
---

# Installation on WSL2

This guide covers installing PostgreSQL 18 on WSL2 (Windows Subsystem for Linux 2) with Ubuntu. WSL2 is the recommended setup for Windows users who want a real Linux development environment.

## Prerequisites

- Windows 10 (build 19041+) or Windows 11
- WSL2 installed with Ubuntu (22.04 LTS or 24.04 LTS)
- At least 4GB RAM

If you don't have WSL2 yet, install it first:

```bash
# In PowerShell (Run as Administrator)
wsl --install
# Restart your computer when prompted
# This installs WSL2 with Ubuntu by default
```

## Option A: Install via APT (Quick, Default Version)

```bash
# Inside WSL2 Ubuntu terminal
sudo apt update
sudo apt install -y postgresql postgresql-contrib

# Start PostgreSQL (WSL2 doesn't use systemd by default)
sudo service postgresql start

# Verify it's running
sudo service postgresql status
```

> [!warning] WSL2 and systemd
> WSL2 doesn't run systemd by default on older Windows builds. If `systemctl` doesn't work, use `sudo service postgresql start` instead. To enable systemd, add to `/etc/wsl.conf`:
> ```ini
> [boot]
> systemd=true
> ```
> Then restart WSL: `wsl --shutdown` in PowerShell, then reopen.

## Option B: Install Official PostgreSQL APT Repo (Specific Version)

To get PostgreSQL 18 specifically (or any version), use the official PostgreSQL APT repository:

```bash
# Add the PostgreSQL APT repository
sudo install -d /usr/share/postgresql-common/pgdg
sudo curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc \
     --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc
sudo sh -c 'echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] \
  https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" \
  > /etc/apt/sources.list.d/pgdg.list'

# Update and install PostgreSQL 18
sudo apt update
sudo apt -y install postgresql-18

# Start the cluster
sudo pg_ctlcluster 18 main start
```

## Option C: Docker (Most Reproducible)

If you prefer Docker (recommended for reproducible environments):

```bash
# Pull and run PostgreSQL 18
docker run -d --name pg18 \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=practice \
  -p 5432:5432 \
  -v pgdata18:/var/lib/postgresql/data \
  postgres:18

# Connect to it
docker exec -it pg18 psql -U postgres -d practice
```

### Docker Compose (with pgAdmin GUI)

Create a `docker-compose.yml`:

```yaml
services:
  db:
    image: postgres:18
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: practice
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d practice"]
      interval: 10s

  pgadmin:
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports: ["5050:80"]
    depends_on: [db]

volumes:
  pgdata:
```

```bash
docker compose up -d
# PostgreSQL on port 5432, pgAdmin on http://localhost:5050
```

## First Connection

After installation, connect to PostgreSQL:

```bash
# Switch to the postgres OS user (created during installation)
sudo -u postgres psql

# You should see the psql prompt:
# psql (18.4)
# Type "help" for help.
# postgres=#
```

### Set a Password for postgres User

```sql
-- Inside psql
ALTER USER postgres PASSWORD 'your_password_here';
\q  -- quit
```

### Create Your Own User and Database

```bash
# As postgres OS user
sudo -u postgres createuser --superuser --pwprompt yourname
sudo -u postgres createdb -O yourname yourname
```

Now you can connect without switching users:

```bash
psql -U yourname -d yourname -h localhost
# Enter your password when prompted
```

## Common Gotchas

### 1. Peer Authentication Failed

```
FATAL: Peer authentication failed for user "postgres"
```

**Cause**: The default `pg_hba.conf` uses "peer" auth for local connections (requires OS username to match database username).

**Fix**: Either use `sudo -u postgres psql`, or edit `pg_hba.conf`:

```bash
# Find pg_hba.conf
sudo -u postgres psql -c "SHOW hba_file;"
# Usually: /etc/postgresql/18/main/pg_hba.conf

# Edit it
sudo nano /etc/postgresql/18/main/pg_hba.conf
# Change "local all postgres peer" to "local all postgres scram-sha-256"
# Change "local all all peer" to "local all all scram-sha-256"

# Reload
sudo systemctl reload postgresql
# or: sudo service postgresql reload
```

### 2. Connection Refused

```
connection refused at localhost:5432
```

**Cause**: PostgreSQL isn't running, or isn't listening on localhost.

**Fix**:
```bash
# Check if running
sudo service postgresql status

# Check listening addresses in postgresql.conf
sudo -u postgres psql -c "SHOW listen_addresses;"
# If empty or 'localhost', and you're connecting from Windows, ensure:
# listen_addresses = 'localhost' (or '*' for all)
# Also check port: SHOW port;
```

### 3. Multiple Clusters

```bash
# List all PostgreSQL clusters
pg_lsclusters

# Start a specific cluster
sudo pg_ctlcluster 18 main start

# Stop, restart, reload
sudo pg_ctlcluster 18 main stop
sudo pg_ctlcluster 18 main restart
sudo pg_ctlcluster 18 main reload
```

## Verification

```sql
-- Connect and run these to verify your installation
SELECT version();
-- Should show: PostgreSQL 18.x ...

SELECT current_date;
-- Should show today's date

CREATE TABLE test (id serial PRIMARY KEY, name text);
INSERT INTO test (name) VALUES ('Hello PostgreSQL');
SELECT * FROM test;
DROP TABLE test;
```

## What's Next

- [[01-Foundations/03-psql-Basics|psql Basics]] — learn the command-line tool
- [[01-Foundations/04-Creating-Database-Tables|Creating Databases and Tables]]
- [[01-Foundations/05-Data-Types|Data Types]]

## External Resources

- [Official Install Guide (Ubuntu)](https://www.postgresql.org/download/linux/ubuntu/)
- [Docker Hub PostgreSQL](https://hub.docker.com/_/postgres)
- [WSL2 Documentation](https://learn.microsoft.com/en-us/windows/wsl/)
