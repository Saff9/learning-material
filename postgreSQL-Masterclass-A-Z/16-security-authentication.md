# 16 - Security & Authentication

> Roles, privileges, RLS, SSL, OAuth 2.0 (PG 18), encryption, and audit logging.

---

## Role-Based Access Control

```sql
-- Create roles
CREATE ROLE app_readonly WITH LOGIN PASSWORD 'SecurePass1!';
CREATE ROLE app_readwrite WITH LOGIN PASSWORD 'SecurePass2!';
CREATE ROLE app_migration WITH LOGIN PASSWORD 'SecurePass3!';

-- Grant database access
GRANT CONNECT ON DATABASE appdb TO app_readonly;
GRANT CONNECT ON DATABASE appdb TO app_readwrite;

-- Grant schema usage
GRANT USAGE ON SCHEMA public TO app_readonly;
GRANT USAGE, CREATE ON SCHEMA public TO app_readwrite;

-- Grant table privileges
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_readwrite;

-- Default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO app_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_readwrite;

-- Grant sequence usage
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_readwrite;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON SEQUENCES TO app_readwrite;

-- Role inheritance
GRANT app_readonly TO app_readwrite;
GRANT app_readwrite TO app_migration;
```

---

## Row-Level Security (RLS)

```sql
-- Enable RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY doc_owner_policy ON documents
    FOR ALL
    TO app_readwrite
    USING (owner_id = current_setting('app.current_user_id')::INTEGER);

-- Bypass RLS for admin
ALTER TABLE documents FORCE ROW LEVEL SECURITY;
-- Superusers and table owners bypass unless FORCE is set

-- Multiple policies
CREATE POLICY doc_public_policy ON documents
    FOR SELECT
    TO app_readonly
    USING (is_public = TRUE);

-- Set user context
SET app.current_user_id = '42';
SELECT * FROM documents;  -- Only sees docs where owner_id = 42
```

---

## Authentication Methods

### pg_hba.conf

```conf
# Local
local   all             all                                     scram-sha-256

# IPv4
hostssl all             all             127.0.0.1/32            scram-sha-256

# Application servers
hostssl appdb           app_readwrite   10.0.1.0/24             scram-sha-256
hostssl appdb           app_readonly    10.0.2.0/24             scram-sha-256

# Reject rest
host    all             all             0.0.0.0/0               reject
```

### OAuth 2.0 (PostgreSQL 18)

```conf
# New in PG 18: OAuth 2.0 authentication
# Requires a validator module to verify bearer tokens
hostssl all             all             0.0.0.0/0               oauth2
```

### LDAP

```conf
hostssl all             all             0.0.0.0/0               ldap
ldapserver=ldap.example.com
ldapport=636
ldapbinddn="cn=postgres,dc=example,dc=com"
ldapbindpasswd="secret"
ldapbasedn="dc=example,dc=com"
ldapsearchattribute="uid"
```

---

## SSL/TLS

```conf
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
ssl_ca_file = '/etc/ssl/certs/ca.crt'
ssl_crl_file = ''
ssl_ciphers = 'HIGH:!aNULL:!MD5'
ssl_min_protocol_version = 'TLSv1.2'
```

---

## Encryption

```sql
-- Column-level encryption with pgcrypto
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt
INSERT INTO secrets (data) 
VALUES (pgp_sym_encrypt('sensitive data', 'encryption-key'));

-- Decrypt
SELECT pgp_sym_decrypt(data, 'encryption-key') FROM secrets;

-- Hash passwords
SELECT crypt('user_password', gen_salt('bf', 10));

-- Verify password
SELECT * FROM users WHERE password_hash = crypt('input_password', password_hash);
```

---

## Audit Logging

```sql
-- Enable pgaudit extension
CREATE EXTENSION IF NOT EXISTS pgaudit;

-- Configure
ALTER SYSTEM SET pgaudit.log = 'write, ddl';
ALTER SYSTEM SET pgaudit.log_catalog = off;
SELECT pg_reload_conf();

-- Or use trigger-based audit
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    table_name TEXT,
    action TEXT,
    record_id BIGINT,
    old_data JSONB,
    new_data JSONB,
    changed_by TEXT DEFAULT CURRENT_USER,
    changed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

---
*Previous: 15 - Partitioning | Next: 17 - Backup & Recovery*
