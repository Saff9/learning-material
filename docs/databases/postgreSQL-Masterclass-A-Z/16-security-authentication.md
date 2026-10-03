# 16 - Security & Authentication

> Comprehensive deep dive into Role-Based Access Control (RBAC), Row-Level Security (RLS), Authentication (pg_hba.conf), SSL/TLS, and Audit Logging.

---

## Role-Based Access Control (RBAC)

In PostgreSQL, Users and Groups are unified into a single concept: **Roles**. A role with `LOGIN` privilege acts like a user. A role without it acts like a group.

### Role Attributes and Creation
```sql
-- High privilege role (Use sparingly!)
CREATE ROLE db_admin WITH SUPERUSER CREATEDB CREATEROLE LOGIN PASSWORD 'AdminPass!';

-- Typical Application Roles
-- 1. Group role (No login)
CREATE ROLE app_readonly;
CREATE ROLE app_readwrite;
CREATE ROLE app_migration;

-- 2. User roles
CREATE USER reporting_user WITH PASSWORD 'SecurePass1!';
CREATE USER api_backend WITH PASSWORD 'SecurePass2!';

-- 3. Assign Users to Groups (Inheritance)
GRANT app_readonly TO reporting_user;
GRANT app_readwrite TO api_backend;
```

### Granting Privileges
Permissions must be explicitly granted. By default, users cannot even connect to databases they didn't create.

```sql
-- 1. Database level
GRANT CONNECT ON DATABASE appdb TO app_readonly, app_readwrite;

-- 2. Schema level
GRANT USAGE ON SCHEMA public TO app_readonly, app_readwrite;
GRANT CREATE ON SCHEMA public TO app_migration;

-- 3. Table/Object level
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_readwrite;

-- 4. Sequences (Often forgotten, required for SERIAL/IDENTITY INSERTs!)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_readwrite;
```

### Default Privileges
The `GRANT` commands above only apply to *existing* tables. If `app_migration` creates a new table, `app_readwrite` won't have access. You must alter default privileges:

```sql
ALTER DEFAULT PRIVILEGES FOR ROLE app_migration IN SCHEMA public 
    GRANT SELECT ON TABLES TO app_readonly;

ALTER DEFAULT PRIVILEGES FOR ROLE app_migration IN SCHEMA public 
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_readwrite;

ALTER DEFAULT PRIVILEGES FOR ROLE app_migration IN SCHEMA public 
    GRANT USAGE, SELECT ON SEQUENCES TO app_readwrite;
```

---

## Row-Level Security (RLS)

RLS allows you to control access to specific *rows* based on the user executing the query or session context variables. Absolutely critical for Multi-Tenant SaaS applications.

```sql
-- 1. Enable RLS on the table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 2. Create policies
-- Only allow the owner to see and edit their documents
CREATE POLICY doc_tenant_isolation ON documents
    FOR ALL
    TO app_readwrite
    USING (tenant_id = current_setting('app.current_tenant')::UUID);

-- Allow public read access if the document is marked public
CREATE POLICY doc_public_read ON documents
    FOR SELECT
    TO app_readonly
    USING (is_public = TRUE);

-- 3. Bypassing RLS
-- Superusers and table owners bypass RLS by default. To force RLS on table owners:
ALTER TABLE documents FORCE ROW LEVEL SECURITY;

-- 4. Application Context Usage
-- The backend API authenticates the user, then sets the context before querying:
SET LOCAL app.current_tenant = 'a1b2c3d4-e5f6-7890-1234-56789abcdef0';
SELECT * FROM documents;  -- Magic! Only returns rows for this tenant.
```

---

## Authentication Configuration (pg_hba.conf)

The `pg_hba.conf` (Host-Based Authentication) file controls who can connect, from where, and how they authenticate.
Rules are read sequentially; the first matching rule applies.

```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local unix socket (passwordless trust for root/postgres)
local   all             postgres                                peer

# Require encrypted passwords (SCRAM-SHA-256) for all IPv4 connections
hostssl all             all             0.0.0.0/0               scram-sha-256

# Specific application subnets
hostssl appdb           api_backend     10.0.1.0/24             scram-sha-256

# Reject all other access
host    all             all             0.0.0.0/0               reject

# Active Directory / LDAP Integration
hostssl all             all             10.0.2.0/24             ldap ldapserver=ad.company.local ldapport=636 ldapbinddn="CN=pg_svc,OU=ServiceAccounts,DC=company,DC=local" ldapbindpasswd="secret" ldapbasedn="OU=Users,DC=company,DC=local" ldapsearchattribute="sAMAccountName"
```
**CRITICAL:** Always use `scram-sha-256` in PostgreSQL 14+. It is significantly more secure than `md5` against brute force and man-in-the-middle attacks. Update `password_encryption = scram-sha-256` in `postgresql.conf`.

---

## SSL/TLS Setup

```conf
# postgresql.conf
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
ssl_ca_file = '/etc/ssl/certs/ca.crt'
ssl_ciphers = 'HIGH:!aNULL:!MD5'
ssl_prefer_server_ciphers = on
ssl_min_protocol_version = 'TLSv1.2' # Enforce TLS 1.2 or 1.3
```

---

## Data Encryption at Rest (pgcrypto)

While file-system level encryption (LUKS/EBS) is standard, sometimes specific PII columns need database-level encryption.

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt sensitive data using symmetric key
INSERT INTO secrets (secret_data) 
VALUES (pgp_sym_encrypt('API_KEY_12345', 'super_secret_master_key'));

-- Decrypt
SELECT pgp_sym_decrypt(secret_data::bytea, 'super_secret_master_key') FROM secrets;

-- Hashing passwords (if not using an external auth provider like Auth0/Cognito)
-- Note: It is better to use modern algorithms inside your application code (Argon2, bcrypt).
INSERT INTO users (password_hash) VALUES (crypt('user_pass', gen_salt('bf', 10)));
SELECT * FROM users WHERE password_hash = crypt('input_pass', password_hash);
```

---

## Audit Logging

Tracking who did what, and when, is required for compliance (SOC2, HIPAA).

### 1. Simple Built-in Logging (postgresql.conf)
```conf
logging_collector = on
log_statement = 'ddl'    # Log all schema modifications (CREATE/ALTER/DROP)
# log_statement = 'all'  # Warning: Massive I/O and disk space usage!
log_connections = on
log_disconnections = on
```

### 2. Comprehensive Auditing (pgAudit Extension)
`pgAudit` provides detailed session and object audit logging via standard PG logging facilities.

```sql
-- Requires shared_preload_libraries = 'pgaudit' in postgresql.conf
CREATE EXTENSION pgaudit;

-- Audit all reads and writes
ALTER SYSTEM SET pgaudit.log = 'read, write, ddl';
SELECT pg_reload_conf();
```

### 3. Row-level Trigger Audit (For Data History)
If you need to query historical changes within the database itself.

```sql
CREATE TABLE audit_log (
    audit_id BIGSERIAL PRIMARY KEY,
    table_name TEXT,
    action VARCHAR(10),
    old_data JSONB,
    new_data JSONB,
    changed_by TEXT DEFAULT CURRENT_USER,
    changed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE FUNCTION trigger_audit() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (table_name, action, old_data, new_data)
    VALUES (
        TG_TABLE_NAME, 
        TG_OP, 
        (CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN to_jsonb(OLD) ELSE NULL END),
        (CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN to_jsonb(NEW) ELSE NULL END)
    );
    RETURN NULL; -- AFTER trigger
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---
*Previous: 15 - Partitioning | Next: 17 - Backup & Recovery*
