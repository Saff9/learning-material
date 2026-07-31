---
tags: [postgresql, extensions, reference]
---

# Other Useful Extensions

## uuid-ossp — UUID Generation

```sql
CREATE EXTENSION "uuid-ossp";
SELECT uuid_generate_v4();  -- random UUID
-- Note: PostgreSQL 13+ has gen_random_uuid() built-in (no extension needed)
```

## pgcrypto — Encryption

```sql
CREATE EXTENSION pgcrypto;

-- Hash a password (bcrypt)
SELECT crypt('mypassword', gen_salt('bf', 12));

-- Verify
SELECT crypt('mypassword', '$2a$12$...') = '$2a$12$...';  -- true if matches

-- Encrypt data
SELECT pgp_sym_encrypt('secret data', 'mykey');
SELECT pgp_sym_decrypt(encrypted_data, 'mykey');
```

## hstore — Key-Value Store

```sql
CREATE EXTENSION hstore;

CREATE TABLE products (id SERIAL PRIMARY KEY, attrs hstore);
INSERT INTO products (attrs) VALUES ('color=>red, size=>large');
SELECT attrs->'color' FROM products;
SELECT * FROM products WHERE attrs @> 'color=>red';
```

## citext — Case-Insensitive Text

```sql
CREATE EXTENSION citext;
CREATE TABLE users (email citext UNIQUE);
INSERT INTO users (email) VALUES ('Alice@Example.com');
-- This would conflict (citext is case-insensitive):
-- INSERT INTO users (email) VALUES ('alice@example.com');
```

## timescaledb — Time-Series

```sql
CREATE EXTENSION timescaledb;

CREATE TABLE metrics (time TIMESTAMPTZ, device_id INT, value FLOAT);
SELECT create_hypertable('metrics', 'time');
```

## pg_partman — Partition Management

```sql
CREATE EXTENSION pg_partman;
-- Automates creation and cleanup of time-based partitions
```

## pg_repack — Online Bloat Removal

```bash
# Removes bloat without exclusive locks (unlike VACUUM FULL)
pg_repack -h host -U postgres -d myapp -t big_table
```

## hypopg — Hypothetical Indexes

```sql
CREATE EXTENSION hypopg;

-- Test if an index would help WITHOUT actually creating it
SELECT hypopg_create_index('CREATE INDEX ON users(email)');
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';
-- If plan improves, create the real index

SELECT hypopg_reset();  -- discard virtual indexes
```

## Next

- [[07-Application-Integration/01-Python-psycopg2|Python Integration]]
- [[11-Resources/|Resources]]
