---
tags: [postgresql, admin, security, roles, permissions]
---

# Users, Roles, and Permissions

PostgreSQL uses "roles" for both users and groups. A "user" is just a role with LOGIN privilege.

## Creating Roles

```sql
-- Create a login role (user)
CREATE ROLE appuser WITH LOGIN PASSWORD 'secret' VALID UNTIL '2026-12-31';

-- Create a group role (no login)
CREATE ROLE analytics_team;

-- Add user to group
GRANT analytics_team TO appuser;

-- Create a superuser (use sparingly!)
CREATE ROLE admin WITH LOGIN SUPERUSER PASSWORD 'adminpw';
```

## Granting Privileges

```sql
-- Database level
GRANT CONNECT ON DATABASE myapp TO appuser;
GRANT ALL ON DATABASE myapp TO admin;

-- Schema level
GRANT USAGE ON SCHEMA public TO appuser;
GRANT CREATE ON SCHEMA public TO appuser;

-- Table level
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO appuser;

-- Column level (restrict to specific columns)
GRANT SELECT (id, name, email) ON users TO analytics_team;

-- Sequence level (needed for SERIAL/IDENTITY columns)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO appuser;

-- Future tables (apply to tables created later)
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO analytics_team;
```

## Revoking

```sql
REVOKE ALL ON users FROM public;
REVOKE INSERT, UPDATE, DELETE ON users FROM appuser;
REVOKE analytics_team FROM appuser;
```

## Row-Level Security (RLS)

```sql
-- Enable RLS
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

-- Force RLS even for table owner
ALTER TABLE invoices FORCE ROW LEVEL SECURITY;

-- Policy: users can only see their own rows
CREATE POLICY invoices_owner_select ON invoices
    FOR SELECT USING (owner = current_user);

-- Policy: users can only update their own rows
CREATE POLICY invoices_owner_update ON invoices
    FOR UPDATE USING (owner = current_user)
    WITH CHECK (owner = current_user);

-- Policy: managers can see all
CREATE POLICY invoices_manager_all ON invoices
    FOR ALL TO managers USING (true) WITH CHECK (true);
```

## pg_hba.conf — Host-Based Authentication

```conf
# TYPE  DATABASE  USER    ADDRESS         METHOD
local   all       all                     peer
hostssl all       all     0.0.0.0/0        scram-sha-256
host    all       all     127.0.0.1/32     scram-sha-256
```

## Useful Queries

```sql
-- List all roles
\du

-- Show current user
SELECT current_user;

-- Show all privileges on a table
\dp users

-- List all grants
SELECT grantee, table_schema, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE table_name = 'users';
```

## Next

- [[05-Administration/02-Backup-Recovery|Backup and Recovery]]
- [[05-Administration/03-Replication|Replication]]
